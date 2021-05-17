drop table stoppedReservs id EXISTS;
CREATE TABLE stoppedReservs(  
    id int NOT NULL primary key AUTO_INCREMENT comment 'primary key',
    startTime DATETIME,
    endTime DATETIME,
) default charset utf8 comment '';