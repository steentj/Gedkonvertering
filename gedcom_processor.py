
import sys
import site
print(f"Python executable: {sys.executable}")
print(f"Python path: {sys.path}")
print(f"Site packages: {site.getsitepackages()}")


from typing import Dict, Optional, Tuple, List, NamedTuple
import os
import argparse
from docx import Document
from docx.shared import Inches, Pt, Cm
from docx.enum.section import WD_ORIENTATION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

class Individual:
    def __init__(self, id: str):
        self.id = id
        self.name = ""
        self.birth_date = ""
        self.death_date = ""
        self.father_id = None
        self.mother_id = None

class GedcomProcessor:
    def __init__(self, gedcom_file: str):
        self.individuals: Dict[str, Individual] = {}
        self.person_numbers: Dict[str, int] = {}
        self.current_number = 1
        self._parse_gedcom(gedcom_file)
    
    def _parse_gedcom(self, gedcom_file: str):
        current_indi = None
        current_event = None
        current_family = None
        child_id = None
        
        with open(gedcom_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(' ', 2)
                if len(parts) < 2:
                    continue
                    
                level = int(parts[0])
                tag_or_id = parts[1]
                remaining = parts[2] if len(parts) > 2 else ""
                
                # Handle INDI records
                if level == 0:
                    if remaining == "INDI":
                        # Format: 0 @ID@ INDI
                        current_indi = Individual(tag_or_id)
                        self.individuals[tag_or_id] = current_indi
                        current_event = None
                    elif remaining == "FAM":
                        # Format: 0 @ID@ FAM
                        current_indi = None
                        current_event = None
                        current_family = tag_or_id
                    else:
                        current_indi = None
                        current_event = None
                        current_family = None
                
                elif current_indi and level == 1:
                    if tag_or_id == "NAME":
                        current_indi.name = remaining.replace('/', '').strip()
                    elif tag_or_id in ["BIRT", "DEAT"]:
                        current_event = tag_or_id
                    elif tag_or_id == "FAMC":
                        # Child in family
                        pass
                
                elif current_indi and level == 2:
                    if tag_or_id == "DATE" and current_event:
                        if current_event == "BIRT":
                            current_indi.birth_date = remaining
                        elif current_event == "DEAT":
                            current_indi.death_date = remaining
                
                elif current_family and level == 1:
                    if tag_or_id == "CHIL":
                        child_id = remaining
                    elif tag_or_id == "HUSB" and child_id:
                        # Found father
                        father_id = remaining
                        if child_id in self.individuals:
                            self.individuals[child_id].father_id = father_id
                    elif tag_or_id == "WIFE" and child_id:
                        # Found mother
                        mother_id = remaining
                        if child_id in self.individuals:
                            self.individuals[child_id].mother_id = mother_id

    def get_person_info(self, person: Individual) -> str:
        if person.id not in self.person_numbers:
            self.person_numbers[person.id] = self.current_number
            self.current_number += 1
            
        number = self.person_numbers[person.id]
        info = f"{number}. {person.name}"
        if person.birth_date:
            info += f" (f. {person.birth_date}"
            if person.death_date:
                info += f", d. {person.death_date}"
            info += ")"
        return info

    def find_parents(self, person: Individual) -> Tuple[Optional[Individual], Optional[Individual]]:
        father = self.individuals.get(person.father_id) if person.father_id else None
        mother = self.individuals.get(person.mother_id) if person.mother_id else None
        return father, mother

    def set_cell_vertical_text(self, cell):
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        textDirection = OxmlElement('w:textDirection')
        textDirection.set(qn('w:val'), 'btLr')
        tcPr.append(textDirection)

    def generate_word_grid(self, doc: Document, root_person: Individual, depth: int = 4):
        # Set landscape orientation
        section = doc.sections[0]
        section.orientation = WD_ORIENTATION.LANDSCAPE
        section.page_width = Cm(29.7)  # A4 height
        section.page_height = Cm(21.0)  # A4 width
        
        table = doc.add_table(rows=depth, cols=2 ** (depth - 1))
        table.style = 'Table Grid'
        table.allow_autofit = True
        table.width = Inches(11)
        
        for generation in range(depth):
            cells = [""] * (2 ** generation)
            stack = [(root_person, 0)]
            cell_index = 0
            
            while stack and cell_index < len(cells):
                person, gen = stack.pop(0)
                if gen == generation:
                    if person:
                        cells[cell_index] = self.get_person_info(person)
                    cell_index += 1
                elif person:
                    father, mother = self.find_parents(person)
                    stack.append((mother, gen + 1))
                    stack.append((father, gen + 1))
            
            row = table.rows[generation]
            cells_per_column = (2 ** (depth - 1)) // (2 ** generation)
            for i, cell_text in enumerate(cells):
                start_col = i * cells_per_column
                end_col = (i + 1) * cells_per_column
                if start_col < end_col:
                    if cells_per_column > 1:
                        cell = row.cells[start_col]
                        for col in range(start_col + 1, end_col):
                            cell.merge(row.cells[col])
                    
                    cell = row.cells[start_col]
                    cell.text = cell_text
                    
                    if generation == depth - 1:
                        self.set_cell_vertical_text(cell)
                        tc = cell._tc
                        tc.height = Cm(8)
                    
                    paragraph = cell.paragraphs[0]
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    
                    run = paragraph.runs[0] if paragraph.runs else paragraph.add_run()
                    font_size = 12 - generation
                    run.font.size = Pt(max(8, font_size))
        
        doc.add_paragraph('')

    def process_tree(self, root_person: Individual, output_dir: str = "output", format: str = "markdown"):
        os.makedirs(output_dir, exist_ok=True)
        
        stack = [(root_person, 1)]
        processed = set()
        
        while stack:
            person, number = stack.pop(0)
            if not person or person.id in processed:
                continue
                
            processed.add(person.id)
            
            if format == "word":
                doc = Document()
                doc.add_heading(f'Anetavle for person {number}', 0)
                self.generate_word_grid(doc, person)
                filename = f"{output_dir}/{number}.docx"
                doc.save(filename)
            
            father, mother = self.find_parents(person)
            if father:
                stack.append((father, number * 2))
            if mother:
                stack.append((mother, number * 2 + 1))

def main():
    parser = argparse.ArgumentParser(description='Process a GEDCOM file and generate ancestor trees')
    parser.add_argument('gedcom_file', help='Path to the GEDCOM file to process')
    parser.add_argument('--output-dir', default='output', help='Directory to store output files (default: output)')
    parser.add_argument('--format', choices=['markdown', 'word'], default='markdown',
                      help='Output format: markdown (.md) or Word (.docx) (default: markdown)')
    args = parser.parse_args()

    print(f"Processing GEDCOM file: {args.gedcom_file}")
    processor = GedcomProcessor(args.gedcom_file)
    print(processor.individuals)
    
    print(f"Found {len(processor.individuals)} individuals")
    
    # Find a root person (first person in the file)
    root_person = next(iter(processor.individuals.values())) if processor.individuals else None
    
    if root_person:
        processor.process_tree(root_person, args.output_dir, args.format)
        print(f"Generated ancestor trees in {args.output_dir}/")
    else:
        print("No individuals found in the GEDCOM file")

if __name__ == "__main__":
    main()