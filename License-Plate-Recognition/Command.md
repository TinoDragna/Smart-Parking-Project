pip install -r ./requirement.txt

pip install mysql-connector-python

python webcam.py 
python webcam2.py 

python upWeb.py             #ctrl+c to exitq





CREATE TABLE `VehiclePlate` (
  `PlateID` bigint(20) NOT NULL AUTO_INCREMENT,
  `VehiclePlate` varchar(20) NOT NULL,   -- Tên cột thống nhất với bảng rfidcard
  `RFID` varchar(20) DEFAULT NULL,       -- Liên kết với rfidcard
  `Status` varchar(15) DEFAULT NULL,     -- MATCHED / UNAUTHORIZED
  `TimeStamp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`PlateID`),
  KEY `RFID` (`RFID`),
  CONSTRAINT `VehiclePlate_ibfk_1` FOREIGN KEY (`RFID`) REFERENCES `rfidcard` (`RFID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

