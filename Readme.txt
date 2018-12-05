Instruction to run the application :

*****************
Install Following Python Libraries using pip :
Eg. pip install library_name
- flask
- flask_wtf
- PIL
- numpy
- pymysql

*****************
Install MySql Server
Link - https://dev.mysql.com/downloads/mysql/


============================================================================================
*****************
-Create Database IN MYSQL
database name : myflaskapp
change hostname,username,password,databasename in each views Function

Following Tables Should be Created :
drop table USERS;
drop table ARTICLES;
commit;


**USERS TABLE CREATION QUERIES**

CREATE TABLE USERS (ID INTEGER primary key auto_increment,
NAME VARCHAR(100),
EMAIL VARCHAR(100),
USERNAME VARCHAR(30),
PASSWORD VARCHAR(30),
REGISTER_DATE TIMESTAMP DEFAULT current_timestamp
);



**ARTICLES TABLE CREATION QUERIES**

CREATE TABLE ARTICLES (ID INT(11) PRIMARY KEY auto_increment,
TITLE VARCHAR(255),
AUTHOR VARCHAR(255),
BODY TEXT,
CREATE_DATE TIMESTAMP DEFAULT current_timestamp
);

commit;

============================================================================================





