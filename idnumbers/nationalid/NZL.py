from .nzl.driver_license import DriverLicenseNumber as DriverLicenseNumber
from .nzl.inland_revenue_department import InlandRevenueDepartmentNumber as InlandRevenueDepartmentNumber
from .nzl.passport import PassportNumber as PassportNumber
from .nzl.health_index import NationalHealthIndexNumber as NationalHealthIndexNumber
from .util import alias_of

NationalID = alias_of(DriverLicenseNumber)
