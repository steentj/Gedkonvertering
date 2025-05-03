import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from gedcom_processor import GedcomProcessor
from tests.test_data import simple_persons_ged, real_persons_ged

 
def test_read_individuals_simple(simple_persons_ged):
    print("Running test_read_individuals_simple")
    processor = GedcomProcessor("")
    individuals = processor.read_individuals(simple_persons_ged)
    
    assert len(individuals) == 2
    
    # Test first individual
    assert "@I1@" in individuals
    assert individuals["@I1@"].name == "John Doe"
    assert individuals["@I1@"].birth_date == "1 JAN 1900"
    assert individuals["@I1@"].death_date == "1 DEC 1970"
    
    # Test second individual
    assert "@I2@" in individuals
    assert individuals["@I2@"].name == "Jane Smith"
    assert individuals["@I2@"].birth_date == "1 FEB 1910"
    assert individuals["@I2@"].death_date == ""

def test_read_individuals_real(real_persons_ged):
    print("Running test_read_individuals_real")
    processor = GedcomProcessor("")
    individuals = processor.read_individuals(real_persons_ged)
    
    assert len(individuals) == 3
    
    # Test first individual
    assert "@73626234@" in individuals
    assert individuals["@73626234@"].name == "Erik Thrane Jacobsen"
    assert individuals["@73626234@"].birth_date == "28.10.1916"
    assert individuals["@73626234@"].death_date == "24.04.1987"
    
    # Test second individual
    assert "@3082786@" in individuals
    assert individuals["@3082786@"].name == "Hans Severin Rafn Jorgensen"
    assert individuals["@3082786@"].birth_date == "31.01.1841"
    assert individuals["@3082786@"].death_date == ""
    
    # Test third individual
    assert "@9397319@" in individuals
    assert individuals["@9397319@"].name == "Steen Thrane Jacobsen"
    assert individuals["@9397319@"].birth_date == "06.02.1956"
    assert individuals["@9397319@"].death_date == ""

def test_read_individuals_empty_file(tmp_path):
    print("Running test_read_individuals_empty_file")
    empty_file = tmp_path / "empty.ged"
    empty_file.write_text("")
    
    processor = GedcomProcessor(str(empty_file))
    individuals = processor.read_individuals(str(empty_file))
    
    assert len(individuals) == 0

def test_read_individuals_malformed_data(tmp_path):
    print("Running test_read_individuals_malformed_data")
    malformed_content = """0 INVALID
1 BAD DATA
NOT VALID GEDCOM"""
    
    malformed_file = tmp_path / "malformed.ged"
    malformed_file.write_text(malformed_content)
    
    processor = GedcomProcessor(str(malformed_file))
    individuals = processor.read_individuals(str(malformed_file))
    
    assert len(individuals) == 0