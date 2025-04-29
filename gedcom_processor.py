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
        from tree_processor import TreeProcessor  # Local import to avoid circular dependency
        tree_processor = TreeProcessor(processor)
        tree_processor.process_tree(root_person, args.output_dir, args.format)
        print(f"Generated ancestor trees in {args.output_dir}/")
    else:
        print("No individuals found in the GEDCOM file")

if __name__ == "__main__":
    main()