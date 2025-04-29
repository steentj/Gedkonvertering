from markdown_generator import MarkdownGenerator

class TreeProcessor:
    def __init__(self, gedcom_processor):
        self.gedcom_processor = gedcom_processor
        self.word_generator = WordDocumentGenerator(gedcom_processor)  # Initialize WordDocumentGenerator
        self.markdown_generator = MarkdownGenerator(gedcom_processor)  # Initialize MarkdownGenerator

    def process_tree(self, root_person, output_dir: str = "output", format: str = "markdown"):
        import os
        from docx import Document
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
                self.word_generator.generate_word_grid(doc, person)
                filename = f"{output_dir}/{number}.docx"
                doc.save(filename)
            elif format == "markdown":
                self.markdown_generator.generate_markdown(person, number, output_dir)

            father, mother = self.gedcom_processor.find_parents(person)
            if father:
                stack.append((father, number * 2))
            if mother:
                stack.append((mother, number * 2 + 1))