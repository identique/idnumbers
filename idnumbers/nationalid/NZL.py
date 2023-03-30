from .nzl.driver_license import DriverLicenseNumber
from .nzl.inland_revenue_department import InlandRevenueDepartmentNumber
from .nzl.passport import PassportNumber
from .nzl.health_index import NationalHealthIndexNumber
from .util import alias_of

NationalID = alias_of(DriverLicenseNumber)
