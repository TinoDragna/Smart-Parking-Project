-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Máy chủ: 127.0.0.1
-- Thời gian đã tạo: Th6 15, 2026 lúc 09:26 AM
-- Phiên bản máy phục vụ: 10.4.24-MariaDB
-- Phiên bản PHP: 7.4.29

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Cơ sở dữ liệu: `smart_parking`
--

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `rfidcard`
--

CREATE TABLE `rfidcard` (
  `RFID` varchar(20) NOT NULL,
  `OwnerName` varchar(50) CHARACTER SET utf8 DEFAULT NULL,
  `VehiclePlate` varchar(15) DEFAULT NULL,
  `PhoneNumber` varchar(15) DEFAULT NULL,
  `Type` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Đang đổ dữ liệu cho bảng `rfidcard`
--

INSERT INTO `rfidcard` (`RFID`, `OwnerName`, `VehiclePlate`, `PhoneNumber`, `Type`) VALUES
('5E68200E', 'Phạm Nguyễn Bảo Trang', '61K - 7813129', '0665526556', 'SUV'),
('90172383', 'Trương Thị Vân', '93A - 779312', '0125545167', 'Basic'),
('D3E9FD13', 'Phạm Nguyễn Bảo Trang', '61K - 7813129', '0125545167', 'SUV'),
('TESTRFID01', 'Test User', '29T8-2843', '0123456789', 'Test'),
('TESTRFID02', 't2', '24FF786', '234562346', 'Inova'),
('TESTRFID03', 'test3', 'WWWWWWW', '4567897543', 'BMW');

--
-- Chỉ mục cho các bảng đã đổ
--

--
-- Chỉ mục cho bảng `rfidcard`
--
ALTER TABLE `rfidcard`
  ADD PRIMARY KEY (`RFID`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
