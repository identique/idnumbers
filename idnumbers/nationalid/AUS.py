from .aus.driver_license import DriverLicenseNumber
from .aus.medicare import MedicareNumber
from .aus.tax_file import TaxFileNumber
from .util import alias_of


NationalID = alias_of(DriverLicenseNumber)
"""use driver license as national id"""
