from .aus.driver_license import DriverLicenseNumber as DriverLicenseNumber
from .aus.medicare import MedicareNumber as MedicareNumber
from .aus.tax_file import TaxFileNumber as TaxFileNumber
from .util import alias_of


NationalID = alias_of(DriverLicenseNumber)
"""use driver license as national id"""
