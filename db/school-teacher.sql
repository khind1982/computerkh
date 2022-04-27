create TABLE employee (
    EmployeeID int(100) NOT NULL,
    Surname varchar(50) NOT NULL,
    Forename varchar(50) NOT NULL,
    DateOfBirth date NOT NULL,
    AddressLine1 varchar(200) NOT NULL,
    AddressLine2 varchar(200) NOT NULL,
    Town varchar(50) NOT NULL,
    Postcode varchar(15) NOT NULL,
    ContactNumber varchar(50) NOT NULL,
    DepartmentID int(100) NOT NULL,
    QualificationID int(100) NOT NULL
);

create TABLE department(
    DepartmentID int(100) NOT NULL
    DepartmentDescription varchar(20) NOT NULL
);

create TABLE qualification(
    QualificationID int(100) NOT NULL
    QualificationDescription varchar(30) NOT NULL
)
