class MarkdownGenerator:
    def __init__(self, gedcom_processor):
        self.gedcom_processor = gedcom_processor

    def generate_markdown(self, person, number, output_dir):
        filename = f"{output_dir}/{number}.md"
        with open(filename, "w", encoding="utf-8") as md_file:
            md_file.write(f"# Anetavle for person {number}\n\n")
            md_file.write(self.gedcom_processor.get_person_info(person))
            md_file.write("\n")