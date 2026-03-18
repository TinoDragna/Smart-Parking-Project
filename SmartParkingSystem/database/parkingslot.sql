-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 12, 2026 at 09:39 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `smart_parking`
--

-- --------------------------------------------------------

--
-- Table structure for table `parkingslot`
--

CREATE TABLE `parkingslot` (
  `SlotID` int(11) NOT NULL,
  `SlotCode` varchar(10) NOT NULL,
  `Area` varchar(5) DEFAULT NULL,
  `Status` tinyint(4) DEFAULT 0,
  `CurrentRFID` varchar(20) DEFAULT NULL,
  `GridCol` int(11) NOT NULL DEFAULT 0,
  `GridRow` int(11) NOT NULL DEFAULT 0,
  `Direction` varchar(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `parkingslot`
--

INSERT INTO `parkingslot` (`SlotID`, `SlotCode`, `Area`, `Status`, `CurrentRFID`, `GridCol`, `GridRow`, `Direction`) VALUES
(1, '1', 'A', 1, '5E68200E', 1, 4, NULL),
(2, '2', 'A', 1, NULL, 1, 3, NULL),
(3, '3', 'A', 1, NULL, 1, 2, NULL),
(4, '4', 'A', 2, NULL, 1, 1, NULL),
(5, '5', 'A', 1, NULL, 1, 0, NULL),
(6, '1', 'B', 0, NULL, 2, 4, NULL),
(7, '2', 'B', 1, NULL, 2, 3, NULL),
(8, '3', 'B', 1, NULL, 2, 2, NULL),
(9, '4', 'B', 1, NULL, 2, 1, NULL),
(10, '5', 'B', 1, NULL, 2, 0, NULL),
(11, '1', 'C', 1, NULL, 3, 4, NULL),
(12, '2', 'C', 1, NULL, 3, 3, NULL),
(13, '3', 'C', 1, NULL, 3, 2, NULL),
(14, '4', 'C', 2, NULL, 3, 1, NULL),
(15, '5', 'C', 1, NULL, 3, 0, NULL),
(16, '1', 'D', 1, NULL, 4, 4, NULL),
(17, '2', 'D', 2, NULL, 4, 3, NULL),
(18, '3', 'D', 1, NULL, 4, 2, NULL),
(19, '4', 'D', 1, NULL, 4, 1, NULL),
(20, '5', 'D', 1, NULL, 4, 0, NULL),
(25, 'Entry', '', 1, NULL, 0, 5, 'N'),
(26, 'Exit', '', 1, NULL, 5, 5, 'S');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `parkingslot`
--
ALTER TABLE `parkingslot`
  ADD PRIMARY KEY (`SlotID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `parkingslot`
--
ALTER TABLE `parkingslot`
  MODIFY `SlotID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
