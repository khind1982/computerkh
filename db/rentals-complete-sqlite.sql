create table salutation(
	sal_id int(10) NOT NULL,
	salutation varchar(50) NOT NULL,
	gender varchar(50) NOT NULL,
	primary key (sal_id)
	);

insert into  salutation (sal_id, salutation, gender) values
	(1, 'Mr.', 'Male'),
	(2, 'Ms.', 'Female');

create table customer (
 	cust_id int(10) NOT NULL,
 	firstname varchar(50) NOT NULL,
 	surname varchar(50) NOT NULL,
 	dob date NOT NULL,
 	address varchar(255) NOT NULL,
 	sal_id int(10) NOT NULL,
	primary key (cust_id),
	FOREIGN KEY(sal_id) REFERENCES salutation(sal_id)
	);

insert into customer (cust_id, firstname, surname, DOB, address, sal_id) values
	(1, 'Samwise', 'Gamgee', '2993-04-01', '3 Bagshot Row, Hobbiton',	1),
	(2, 'Frodo', 'Baggins', '2997-07-10', 'Bag End, Bagshot Row, Hobbiton',	1),
	(3, 'Rose', 'Cotton', '2995-03-02', 'Bywater, Hobbiton',	2);

create table movie(
	movie_id int(10) NOT NULL,
	movie_name varchar(50) NOT NULL,
	category varchar(50) NOT NULL,
	primary key (movie_id)
  	);

insert into movie(movie_id, movie_name, category) values
	(1, 'Pirates of the Carabbean', 'Action'),
	(2, 'Batman Begins', 'Action'),
	(3, 'The Hobbit part 1', 'Action'),
	(4, 'Miss Congeniality', 'Romance'),
	(5, 'Freddy Got Fingered', 'Comedy');

create table rental(
	rental_id int(10) NOT NULL,
	cust_id int(10) NOT NULL,
	movie_id int(10) NOT NULL,
	rent_date date NOT NULL,
	FOREIGN KEY(cust_id) REFERENCES customer(cust_id),
	FOREIGN KEY(movie_id) REFERENCES movie(movie_id)
	);

insert into rental (rental_id, cust_id, movie_id, rent_date) values
	(1, 1, 1, '3005-01-06'),
	(2, 1, 2, '3005-01-10'),
	(3, 1, 3, '3005-02-11'),
	(4, 2, 3, '3005-03-01'),
	(5, 2, 4, '3005-03-04'),
	(6, 3, 2, '3005-03-07'),
	(7, 3, 5, '3005-04-20'),
	(8, 3, 3, '3005-04-23');





