import pytest
from gedcom_processor import GedcomProcessor
import tempfile
import os

@pytest.fixture
def sample_gedcom():
    content = """0 @I1@ INDI
1 NAME John /Doe/
1 BIRT
2 DATE 1 JAN 1900
1 DEAT
2 DATE 1 DEC 1970
0 @I2@ INDI
1 NAME Jane /Smith/
1 BIRT
2 DATE 1 FEB 1910"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
        f.write(content)
        temp_path = f.name
    
    yield temp_path
    os.unlink(temp_path)

def test_read_individuals(sample_gedcom):
    processor = GedcomProcessor(sample_gedcom)
    individuals = processor.read_individuals(sample_gedcom)
    
    assert len(individuals) == 2
    
    # Test first individual
    assert "@I1@" in individuals
    assert individuals["@I1@"]["name"] == "John Doe"
    assert individuals["@I1@"]["birth_date"] == "1 JAN 1900"
    assert individuals["@I1@"]["death_date"] == "1 DEC 1970"
    
    # Test second individual
    assert "@I2@" in individuals
    assert individuals["@I2@"]["name"] == "Jane Smith"
    assert individuals["@I2@"]["birth_date"] == "1 FEB 1910"
    assert individuals["@I2@"]["death_date"] == ""

def test_read_individuals_empty_file(tmp_path):
    empty_file = tmp_path / "empty.ged"
    empty_file.write_text("")
    
    processor = GedcomProcessor(str(empty_file))
    individuals = processor.read_individuals(str(empty_file))
    
    assert len(individuals) == 0

def test_read_individuals_malformed_data(tmp_path):
    malformed_content = """0 INVALID
1 BAD DATA
NOT VALID GEDCOM"""
    
    malformed_file = tmp_path / "malformed.ged"
    malformed_file.write_text(malformed_content)
    
    processor = GedcomProcessor(str(malformed_file))
    individuals = processor.read_individuals(str(malformed_file))
    
    assert len(individuals) == 0