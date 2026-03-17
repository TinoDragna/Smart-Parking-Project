-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 17, 2026 at 12:15 PM
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
-- Table structure for table `gatelog`
--

CREATE TABLE `gatelog` (
  `LogID` bigint(20) NOT NULL,
  `GateType` varchar(10) DEFAULT NULL,
  `Action` varchar(10) DEFAULT NULL,
  `Time` datetime DEFAULT NULL,
  `TriggeredBy` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `gatelog`
--

INSERT INTO `gatelog` (`LogID`, `GateType`, `Action`, `Time`, `TriggeredBy`) VALUES
(1, 'Đóng', 'Close', '2025-08-06 17:19:52', '5E68200E'),
(2, 'UNKNOWN', 'Open', '2025-08-18 17:24:24', 'SYSTEM'),
(3, 'UNKNOWN', 'Open', '2025-08-18 17:24:46', 'SYSTEM'),
(4, 'ENTRY', 'Close', '2025-08-18 17:25:35', 'SYSTEM'),
(5, 'ENTRY', 'Open', '2025-08-18 17:26:51', 'SYSTEM'),
(6, 'ENTRY', 'Open', '2025-08-18 17:28:50', 'SYSTEM'),
(7, 'ENTRY', 'Open', '2025-08-18 17:34:40', 'SYSTEM'),
(8, 'EXIT', 'ACCEPT', '2025-08-18 12:59:23', '90172383'),
(9, 'EXIT', 'Open', '2025-08-18 17:59:23', 'SYSTEM'),
(10, 'EXIT', 'OPEN', '2025-08-18 17:59:23', 'RFID'),
(11, 'EXIT', 'Close', '2025-08-18 17:59:26', 'SYSTEM'),
(12, 'EXIT', 'CLOSE', '2025-08-18 12:59:26', 'SYSTEM'),
(13, 'ENTRY', 'ACCEPT', '2025-08-18 13:00:08', '90172383'),
(14, 'ENTRY', 'Open', '2025-08-18 18:00:09', 'SYSTEM'),
(15, 'ENTRY', 'OPEN', '2025-08-18 13:00:09', 'RFID'),
(16, 'ENTRY', 'Close', '2025-08-18 18:00:12', 'SYSTEM'),
(17, 'ENTRY', 'CLOSE', '2025-08-18 13:00:12', 'SYSTEM'),
(18, 'ENTRY', 'REJECT', '2025-08-18 13:00:40', 'D3E9FD13'),
(19, 'ENTRY', 'REJECT', '2025-08-18 13:00:45', 'D3E9FD13'),
(20, 'ENTRY', 'ACCEPT', '2025-08-18 13:00:53', '90172383'),
(21, 'ENTRY', 'Open', '2025-08-18 18:00:53', 'SYSTEM'),
(22, 'ENTRY', 'OPEN', '2025-08-18 13:00:53', 'RFID'),
(23, 'ENTRY', 'Close', '2025-08-18 18:00:56', 'SYSTEM'),
(24, 'ENTRY', 'CLOSE', '2025-08-18 13:00:56', 'SYSTEM'),
(25, 'ENTRY', 'ACCEPT', '2025-08-18 13:01:18', '90172383'),
(26, 'ENTRY', 'REJECT', '2025-08-18 13:01:42', 'D3E9FD13'),
(27, 'EXIT', 'REJECT', '2025-08-18 13:02:40', 'F36E5428'),
(28, 'ENTRY', 'Open', '2025-08-20 10:54:56', 'SYSTEM'),
(29, 'ENTRY', 'Close', '2025-08-20 10:54:59', 'SYSTEM'),
(30, 'EXIT', 'Open', '2025-08-20 10:57:35', 'SYSTEM'),
(31, 'EXIT', 'Close', '2025-08-20 10:57:38', 'SYSTEM'),
(32, 'ENTRY', 'ACCEPT', '2025-08-20 09:01:10', '90172383'),
(33, 'ENTRY', 'Open', '2025-08-20 14:01:10', 'SYSTEM'),
(34, 'ENTRY', 'OPEN', '2025-08-20 09:01:10', 'MQTT'),
(35, 'ENTRY', 'Close', '2025-08-20 14:01:13', 'SYSTEM'),
(36, 'ENTRY', 'CLOSE', '2025-08-20 09:01:13', 'SYSTEM'),
(37, 'EXIT', 'ACCEPT', '2025-08-20 09:01:33', '90172383'),
(38, 'EXIT', 'Open', '2025-08-20 14:01:34', 'SYSTEM'),
(39, 'EXIT', 'OPEN', '2025-08-20 09:01:34', 'MQTT'),
(40, 'EXIT', 'Close', '2025-08-20 14:01:37', 'SYSTEM'),
(41, 'EXIT', 'CLOSE', '2025-08-20 09:01:37', 'SYSTEM'),
(42, 'EXIT', 'Open', '2025-08-20 14:01:41', 'SYSTEM'),
(43, 'EXIT', 'OPEN', '2025-08-20 09:01:41', 'RFID'),
(44, 'EXIT', 'Close', '2025-08-20 14:01:44', 'SYSTEM'),
(45, 'EXIT', 'CLOSE', '2025-08-20 09:01:44', 'SYSTEM'),
(46, 'EXIT', 'ACCEPT', '2025-08-20 09:01:49', '90172383'),
(47, 'EXIT', 'Open', '2025-08-20 14:01:49', 'SYSTEM'),
(48, 'EXIT', 'OPEN', '2025-08-20 09:01:49', 'RFID'),
(49, 'EXIT', 'Open', '2025-08-20 14:01:49', 'SYSTEM'),
(50, 'EXIT', 'OPEN', '2025-08-20 09:01:49', 'MQTT'),
(51, 'EXIT', 'Close', '2025-08-20 14:01:52', 'SYSTEM'),
(52, 'EXIT', 'CLOSE', '2025-08-20 09:01:52', 'SYSTEM'),
(53, 'EXIT', 'REJECT', '2025-08-20 09:01:53', '4E51625A'),
(54, 'EXIT', 'ACCEPT', '2025-08-20 09:01:56', '90172383'),
(55, 'EXIT', 'Open', '2025-08-20 14:01:56', 'SYSTEM'),
(56, 'EXIT', 'OPEN', '2025-08-20 09:01:56', 'MQTT'),
(57, 'EXIT', 'Close', '2025-08-20 14:01:59', 'SYSTEM'),
(58, 'EXIT', 'CLOSE', '2025-08-20 09:01:59', 'SYSTEM'),
(59, 'EXIT', 'Open', '2025-08-20 14:02:12', 'SYSTEM'),
(60, 'EXIT', 'OPEN', '2025-08-20 09:02:12', 'RFID'),
(61, 'EXIT', 'Close', '2025-08-20 14:02:15', 'SYSTEM'),
(62, 'EXIT', 'CLOSE', '2025-08-20 09:02:15', 'SYSTEM'),
(63, 'EXIT', 'ACCEPT', '2025-08-20 09:02:24', '90172383'),
(64, 'EXIT', 'Open', '2025-08-20 14:02:24', 'SYSTEM'),
(65, 'EXIT', 'OPEN', '2025-08-20 09:02:24', 'MQTT'),
(66, 'EXIT', 'Close', '2025-08-20 14:02:27', 'SYSTEM'),
(67, 'EXIT', 'CLOSE', '2025-08-20 09:02:27', 'SYSTEM'),
(68, 'EXIT', 'Open', '2025-08-20 14:02:36', 'SYSTEM'),
(69, 'EXIT', 'OPEN', '2025-08-20 09:02:36', 'RFID'),
(70, 'EXIT', 'Close', '2025-08-20 14:02:38', 'SYSTEM'),
(71, 'EXIT', 'CLOSE', '2025-08-20 09:02:39', 'SYSTEM'),
(72, 'EXIT', 'REJECT', '2025-08-20 09:02:48', '4E51625A'),
(73, 'EXIT', 'REJECT', '2025-08-20 09:02:49', '4E51625A'),
(74, 'EXIT', 'REJECT', '2025-08-20 09:02:51', '4E51625A'),
(75, 'EXIT', 'ACCEPT', '2025-08-20 09:02:53', '90172383'),
(76, 'EXIT', 'Open', '2025-08-20 14:02:53', 'SYSTEM'),
(77, 'EXIT', 'OPEN', '2025-08-20 09:02:54', 'MQTT'),
(78, 'EXIT', 'Close', '2025-08-20 14:02:57', 'SYSTEM'),
(79, 'EXIT', 'CLOSE', '2025-08-20 09:02:57', 'SYSTEM'),
(80, 'EXIT', 'REJECT', '2025-08-20 09:02:58', '4E51625A'),
(81, 'EXIT', 'ACCEPT', '2025-08-20 09:03:19', '90172383'),
(82, 'EXIT', 'Open', '2025-08-20 14:03:19', 'SYSTEM'),
(83, 'EXIT', 'OPEN', '2025-08-20 09:03:19', 'MQTT'),
(84, 'EXIT', 'Close', '2025-08-20 14:03:22', 'SYSTEM'),
(85, 'EXIT', 'CLOSE', '2025-08-20 09:03:22', 'SYSTEM'),
(86, 'EXIT', 'ACCEPT', '2025-08-20 09:03:58', '90172383'),
(87, 'EXIT', 'Open', '2025-08-20 14:03:58', 'SYSTEM'),
(88, 'EXIT', 'OPEN', '2025-08-20 09:03:58', 'MQTT'),
(89, 'EXIT', 'Close', '2025-08-20 14:04:01', 'SYSTEM'),
(90, 'EXIT', 'CLOSE', '2025-08-20 09:04:01', 'SYSTEM'),
(91, 'EXIT', 'ACCEPT', '2025-08-20 09:04:12', '90172383'),
(92, 'EXIT', 'Open', '2025-08-20 14:04:12', 'SYSTEM'),
(93, 'EXIT', 'OPEN', '2025-08-20 09:04:12', 'MQTT'),
(94, 'EXIT', 'Close', '2025-08-20 14:04:15', 'SYSTEM'),
(95, 'EXIT', 'CLOSE', '2025-08-20 09:04:15', 'SYSTEM'),
(96, 'EXIT', 'REJECT', '2025-08-20 09:04:17', '4E51625A'),
(97, 'ENTRY', 'OPEN', '2025-12-19 15:38:21', 'TESTRFID01'),
(98, 'EXIT', 'OPEN', '2025-12-19 15:43:29', 'TESTRFID01'),
(99, 'ENTRY', 'OPEN', '2025-12-19 15:55:17', 'TESTRFID01'),
(100, 'EXIT', 'LPR_MISMAT', '2025-12-19 15:56:20', 'TESTRFID01'),
(101, 'EXIT', 'OPEN', '2025-12-19 16:02:09', 'TESTRFID01'),
(102, 'ENTRY', 'OPEN', '2025-12-19 16:08:41', 'TESTRFID01'),
(103, 'EXIT', 'LPR_UNKNOW', '2025-12-19 16:09:28', 'TESTRFID01'),
(104, 'EXIT', 'LPR_FAIL', '2025-12-19 16:20:25', 'TESTRFID01'),
(105, 'EXIT', 'LPR_FAIL', '2025-12-19 16:21:51', 'TESTRFID01'),
(106, 'EXIT', 'OPEN', '2025-12-19 16:27:17', 'TESTRFID01'),
(107, 'ENTRY', 'OPEN', '2025-12-19 16:36:59', 'TESTRFID01'),
(108, 'EXIT', 'LPR_FAIL', '2025-12-19 16:38:07', 'TESTRFID01'),
(109, 'EXIT', 'LPR_MISMAT', '2025-12-19 16:39:46', 'TESTRFID01'),
(110, 'EXIT', 'FACE_MISMA', '2025-12-19 16:42:03', 'TESTRFID01'),
(111, 'EXIT', 'FACE_MISMA', '2025-12-19 16:47:43', 'TESTRFID01'),
(112, 'EXIT', 'LPR_FAIL', '2025-12-19 16:48:00', 'TESTRFID01'),
(113, 'EXIT', 'OPEN', '2025-12-19 16:48:23', 'TESTRFID01'),
(114, 'ENTRY', 'OPEN', '2025-12-19 17:01:36', 'TESTRFID01'),
(115, 'EXIT', 'LPR_MISMAT', '2025-12-19 17:03:02', 'TESTRFID01'),
(116, 'ENTRY', 'LPR_FAIL', '2025-12-19 17:12:22', 'TESTRFID01'),
(117, 'ENTRY', 'LPR_FAIL', '2025-12-19 17:13:28', 'TESTRFID01'),
(118, 'EXIT', 'OPEN', '2025-12-19 17:14:10', 'TESTRFID01'),
(119, 'ENTRY', 'OPEN', '2025-12-19 17:15:10', 'TESTRFID01'),
(120, 'ENTRY', 'OPEN', '2025-12-22 12:19:03', 'TESTRFID01'),
(121, 'EXIT', 'FACE_MISMA', '2025-12-22 12:20:16', 'TESTRFID01'),
(122, 'ENTRY', 'OPEN', '2025-12-22 12:29:37', 'TESTRFID01'),
(123, 'EXIT', 'LPR_MISMAT', '2025-12-22 12:30:06', 'TESTRFID01'),
(124, 'EXIT', 'LPR_MISMAT', '2025-12-22 12:54:40', 'TESTRFID01'),
(125, 'EXIT', 'OPEN', '2025-12-22 13:01:09', 'TESTRFID01'),
(126, 'ENTRY', 'FACE_FAIL', '2025-12-22 13:08:04', 'TESTRFID01'),
(127, 'ENTRY', 'LPR_FAIL', '2025-12-22 15:31:45', '5E68200E'),
(128, 'ENTRY', 'LPR_FAIL', '2025-12-22 15:32:06', '5E68200E'),
(129, 'ENTRY', 'LPR_FAIL', '2025-12-22 15:32:58', '5E68200E'),
(130, 'ENTRY', 'LPR_FAIL', '2025-12-22 15:33:13', '5E68200E'),
(131, 'ENTRY', 'LPR_FAIL', '2025-12-22 15:37:16', '5E68200E'),
(132, 'ENTRY', 'OPEN', '2025-12-22 15:40:36', '5E68200E'),
(133, 'ENTRY', 'ALREADY_IN', '2025-12-22 15:47:12', '5E68200E'),
(134, 'EXIT', 'LPR_FAIL', '2025-12-22 15:47:41', '5E68200E'),
(135, 'EXIT', 'LPR_FAIL', '2025-12-22 15:47:51', '5E68200E'),
(136, 'EXIT', 'LPR_FAIL', '2025-12-22 15:48:58', '5E68200E'),
(137, 'EXIT', 'LPR_MISMAT', '2025-12-22 15:52:02', '5E68200E'),
(138, 'EXIT', 'LPR_MISMAT', '2025-12-22 15:52:26', '5E68200E'),
(139, 'ENTRY', 'OPEN', '2025-12-22 15:55:02', '5E68200E'),
(140, 'ENTRY', 'OPEN', '2025-12-22 15:59:04', '5E68200E'),
(141, 'ENTRY', 'OPEN', '2025-12-22 16:13:27', '5E68200E'),
(142, 'ENTRY', 'OPEN', '2025-12-22 16:14:25', '5E68200E'),
(143, 'ENTRY', 'RFID_INVAL', '2025-12-22 16:15:03', '5E68'),
(144, 'ENTRY', 'RFID_INVAL', '2025-12-22 16:16:35', '5E68200D'),
(145, 'ENTRY', 'RFID_INVAL', '2025-12-22 16:36:38', '5E68200D'),
(146, 'ENTRY', 'ALREADY_IN', '2025-12-22 16:36:51', '5E68200E'),
(147, 'ENTRY', 'ALREADY_IN', '2025-12-22 16:36:59', '5E68200E'),
(148, 'EXIT', 'LPR_FAIL', '2025-12-22 16:37:24', '5E68200E'),
(149, 'EXIT', 'OPEN', '2025-12-22 16:38:10', '5E68200E'),
(150, 'ENTRY', 'OPEN', '2025-12-22 16:40:55', '5E68200E'),
(151, 'ENTRY', 'ALREADY_IN', '2025-12-22 16:41:55', '5E68200E'),
(152, 'EXIT', 'LPR_FAIL', '2025-12-22 16:43:50', 'TESTRFID01'),
(153, 'EXIT', 'LPR_MISMAT', '2025-12-22 16:43:58', 'TESTRFID01'),
(154, 'EXIT', 'OPEN', '2025-12-22 16:44:55', '5E68200E'),
(155, 'ENTRY', 'OPEN', '2025-12-22 16:46:52', '5E68200E'),
(156, 'EXIT', 'LPR_MISMAT', '2025-12-22 16:53:07', '5E68200E'),
(157, 'EXIT', 'FACE_MISMA', '2025-12-22 16:53:52', '5E68200E'),
(158, 'EXIT', 'OPEN', '2025-12-22 17:02:58', '5E68200E'),
(159, 'ENTRY', 'OPEN', '2025-12-22 17:03:31', '5E68200E'),
(160, 'EXIT', 'OPEN', '2025-12-22 17:04:02', '5E68200E'),
(161, 'ENTRY', 'OPEN', '2025-12-22 17:07:36', '5E68200E'),
(162, 'EXIT', 'OPEN', '2025-12-22 17:08:05', '5E68200E'),
(163, 'ENTRY', 'OPEN', '2025-12-22 17:08:27', '5E68200E'),
(164, 'EXIT', 'LPR_MISMAT', '2025-12-22 17:08:45', '5E68200E'),
(165, 'EXIT', 'OPEN', '2025-12-22 17:12:22', '5E68200E'),
(166, 'ENTRY', 'OPEN', '2025-12-22 17:12:42', '5E68200E'),
(167, 'EXIT', 'OPEN', '2025-12-22 17:13:09', '5E68200E'),
(168, 'ENTRY', 'OPEN', '2025-12-22 17:16:25', '5E68200E'),
(169, 'EXIT', 'LPR_MISMAT', '2025-12-22 17:16:45', '5E68200E'),
(170, 'EXIT', 'OPEN', '2025-12-22 17:21:27', '5E68200E'),
(171, 'ENTRY', 'OPEN', '2025-12-22 17:21:50', '5E68200E'),
(172, 'ENTRY', 'ALREADY_IN', '2025-12-22 17:21:58', '5E68200E'),
(173, 'EXIT', 'OPEN', '2025-12-22 17:22:23', '5E68200E'),
(174, 'ENTRY', 'OPEN', '2025-12-22 17:22:44', '5E68200E'),
(175, 'EXIT', 'OPEN', '2025-12-22 17:23:09', '5E68200E'),
(176, 'ENTRY', 'OPEN', '2025-12-22 17:23:31', '5E68200E'),
(177, 'EXIT', 'OPEN', '2025-12-22 17:23:54', '5E68200E'),
(178, 'ENTRY', 'OPEN', '2025-12-22 17:24:10', '5E68200E'),
(179, 'EXIT', 'OPEN', '2025-12-22 17:24:28', '5E68200E'),
(180, 'ENTRY', 'OPEN', '2025-12-23 13:31:25', '5E68200E'),
(181, 'EXIT', 'LPR_MISMAT', '2025-12-23 13:43:50', '5E68200E'),
(182, 'EXIT', 'OPEN', '2025-12-23 13:44:13', '5E68200E'),
(183, 'ENTRY', 'OPEN', '2025-12-23 13:44:28', '5E68200E'),
(184, 'EXIT', 'LPR_MISMAT', '2025-12-23 13:44:49', '5E68200E'),
(185, 'EXIT', 'OPEN', '2025-12-23 13:45:11', '5E68200E'),
(186, 'ENTRY', 'OPEN', '2025-12-23 13:45:38', '5E68200E'),
(187, 'EXIT', 'OPEN', '2025-12-23 13:46:00', '5E68200E'),
(188, 'ENTRY', 'OPEN', '2025-12-23 13:46:23', '5E68200E'),
(189, 'EXIT', 'OPEN', '2025-12-23 13:46:48', '5E68200E'),
(190, 'ENTRY', 'OPEN', '2025-12-23 13:47:14', '5E68200E'),
(191, 'EXIT', 'OPEN', '2025-12-23 13:47:42', '5E68200E'),
(192, 'ENTRY', 'OPEN', '2025-12-23 13:54:01', '5E68200E'),
(193, 'EXIT', 'OPEN', '2025-12-23 13:54:34', '5E68200E'),
(194, 'ENTRY', 'OPEN', '2025-12-23 13:58:06', '5E68200E'),
(195, 'EXIT', 'OPEN', '2025-12-23 13:58:42', '5E68200E'),
(196, 'ENTRY', 'OPEN', '2025-12-23 14:02:47', '5E68200E'),
(197, 'EXIT', 'OPEN', '2025-12-23 14:03:13', '5E68200E'),
(198, 'ENTRY', 'OPEN', '2025-12-23 14:14:07', '5E68200E'),
(199, 'ENTRY', 'ALREADY_IN', '2025-12-23 14:25:02', '5E68200E'),
(200, 'ENTRY', 'ALREADY_IN', '2025-12-23 14:25:29', '5E68200E'),
(201, 'ENTRY', 'ALREADY_IN', '2025-12-23 14:39:41', '5E68200E'),
(202, 'EXIT', 'LPR_MISMAT', '2025-12-23 14:40:11', '5E68200E'),
(203, 'ENTRY', 'ALREADY_IN', '2025-12-23 14:41:29', 'TESTRFID01'),
(204, 'ENTRY', 'ALREADY_IN', '2025-12-23 14:46:18', 'TESTRFID01'),
(205, 'ENTRY', 'OPEN', '2025-12-23 14:46:31', 'TESTRFID02'),
(206, 'ENTRY', 'ALREADY_IN', '2025-12-23 14:46:37', 'TESTRFID02'),
(207, 'ENTRY', 'RFID_INVAL', '2025-12-23 14:46:47', 'TESTRFID03'),
(208, 'ENTRY', 'OPEN', '2025-12-23 14:59:54', 'TESTRFID02'),
(209, 'ENTRY', 'OPEN', '2025-12-23 15:05:30', 'TESTRFID02'),
(210, 'ENTRY', 'ALREADY_IN', '2025-12-23 15:10:29', 'TESTRFID02'),
(211, 'EXIT', 'OPEN', '2025-12-23 15:10:54', 'TESTRFID02'),
(212, 'EXIT', 'NO_ACTIVE_', '2025-12-23 15:22:21', 'TESTRFID02'),
(213, 'ENTRY', 'OPEN', '2025-12-23 15:22:35', 'TESTRFID02'),
(214, 'ENTRY', 'ALREADY_IN', '2025-12-23 15:22:49', 'TESTRFID02'),
(215, 'EXIT', 'OPEN', '2025-12-23 15:23:05', 'TESTRFID02'),
(216, 'EXIT', 'NO_ACTIVE_', '2025-12-23 15:23:15', 'TESTRFID02'),
(217, 'EXIT', 'NO_ACTIVE_', '2025-12-23 15:23:21', 'TESTRFID03'),
(218, 'ENTRY', 'OPEN', '2025-12-23 15:23:33', 'TESTRFID03'),
(219, 'ENTRY', 'ALREADY_IN', '2025-12-23 15:24:51', 'TESTRFID03'),
(220, 'EXIT', 'OPEN', '2025-12-23 15:25:05', 'TESTRFID03'),
(221, 'ENTRY', 'OPEN', '2025-12-23 15:25:20', 'TESTRFID03'),
(222, 'EXIT', 'OPEN', '2025-12-23 15:25:39', 'TESTRFID03'),
(223, 'ENTRY', 'OPEN', '2025-12-23 15:29:39', 'TESTRFID03'),
(224, 'EXIT', 'OPEN', '2025-12-23 15:29:59', 'TESTRFID03'),
(225, 'ENTRY', 'OPEN', '2025-12-23 15:34:08', 'TESTRFID03'),
(226, 'EXIT', 'OPEN', '2025-12-23 15:35:29', 'TESTRFID03'),
(227, 'ENTRY', 'OPEN', '2025-12-23 15:35:43', 'TESTRFID03'),
(228, 'EXIT', 'FACE_MISMA', '2025-12-23 15:36:01', 'TESTRFID03'),
(229, 'ENTRY', 'ALREADY_IN', '2025-12-23 15:36:28', 'TESTRFID03'),
(230, 'EXIT', 'FACE_MISMA', '2025-12-23 15:36:51', 'TESTRFID03'),
(231, 'EXIT', 'OPEN', '2025-12-23 15:41:31', 'TESTRFID03'),
(232, 'ENTRY', 'OPEN', '2025-12-23 15:41:42', 'TESTRFID03'),
(233, 'EXIT', 'OPEN', '2025-12-23 15:42:14', 'TESTRFID03'),
(234, 'ENTRY', 'OPEN', '2025-12-23 15:43:05', 'TESTRFID03'),
(235, 'EXIT', 'OPEN', '2025-12-23 15:44:22', 'TESTRFID03'),
(236, 'ENTRY', 'OPEN', '2025-12-23 15:44:47', 'TESTRFID03'),
(237, 'EXIT', 'FACE_MISMA', '2025-12-23 15:45:48', 'TESTRFID03'),
(238, 'ENTRY', 'OPEN', '2025-12-23 15:46:25', 'TESTRFID02'),
(239, 'EXIT', 'FACE_MISMA', '2025-12-23 15:46:52', 'TESTRFID02'),
(240, 'EXIT', 'FACE_MISMA', '2025-12-23 15:47:13', 'TESTRFID02'),
(241, 'EXIT', 'FACE_MISMA', '2025-12-23 15:48:02', 'TESTRFID02'),
(242, 'ENTRY', 'OPEN', '2025-12-23 16:05:49', ' TESTRFID02'),
(243, 'ENTRY', 'OPEN', '2025-12-23 16:11:06', 'TESTRFID02'),
(244, 'EXIT', 'OPEN', '2025-12-23 16:11:22', 'TESTRFID02'),
(245, 'ENTRY', 'ALREADY_IN', '2025-12-23 16:33:38', 'TESTRFID03'),
(246, 'ENTRY', 'LPR_FAIL', '2025-12-23 16:34:31', 'TESTRFID02'),
(247, 'ENTRY', 'OPEN', '2025-12-23 16:35:20', 'TESTRFID02'),
(248, 'EXIT', 'OPEN', '2025-12-23 16:35:42', 'TESTRFID02'),
(249, 'ENTRY', 'OPEN', '2025-12-23 16:54:03', 'TESTRFID02'),
(250, 'EXIT', 'FACE_MISMA', '2025-12-23 16:54:50', 'TESTRFID02'),
(251, 'EXIT', 'FACE_MISMA', '2025-12-23 16:55:43', 'TESTRFID02'),
(252, 'EXIT', 'FACE_MISMA', '2025-12-23 16:57:14', 'TESTRFID02'),
(253, 'ENTRY', 'LPR_FAIL', '2025-12-24 14:06:57', 'TESTRFID02'),
(254, 'ENTRY', 'LPR_FAIL', '2025-12-24 14:08:12', 'TESTRFID02'),
(255, 'ENTRY', 'LPR_FAIL', '2025-12-24 14:19:26', 'TESTRFID02'),
(256, 'ENTRY', 'OPEN', '2025-12-24 14:19:44', 'TESTRFID02'),
(257, 'EXIT', 'LPR_FAIL', '2025-12-24 14:22:19', 'TESTRFID02'),
(258, 'EXIT', 'LPR_FAIL', '2025-12-24 14:24:13', 'TESTRFID02'),
(259, 'EXIT', 'LPR_FAIL', '2025-12-24 14:24:49', 'TESTRFID02'),
(260, 'EXIT', 'LPR_MISMAT', '2025-12-24 14:25:42', 'TESTRFID02'),
(261, 'EXIT', 'LPR_MISMAT', '2025-12-24 14:26:34', 'TESTRFID02'),
(262, 'EXIT', 'LPR_MISMAT', '2025-12-24 14:34:08', 'TESTRFID02'),
(263, 'EXIT', 'LPR_MISMAT', '2025-12-24 14:34:20', 'TESTRFID02'),
(264, 'EXIT', 'LPR_MISMAT', '2025-12-24 14:34:29', 'TESTRFID02'),
(265, 'EXIT', 'LPR_MISMAT', '2025-12-24 14:34:49', 'TESTRFID02'),
(266, 'ENTRY', 'FACE_FAIL', '2025-12-24 14:36:12', 'TESTRFID02'),
(267, 'ENTRY', 'LPR_FAIL', '2025-12-24 14:36:25', 'TESTRFID02'),
(268, 'ENTRY', 'LPR_FAIL', '2025-12-24 14:36:39', 'TESTRFID02'),
(269, 'ENTRY', 'LPR_FAIL', '2025-12-24 14:37:00', 'TESTRFID02'),
(270, 'ENTRY', 'LPR_FAIL', '2025-12-24 14:37:11', 'TESTRFID02'),
(271, 'ENTRY', 'LPR_FAIL', '2025-12-24 14:37:21', 'TESTRFID02'),
(272, 'ENTRY', 'OPEN', '2025-12-24 14:38:30', 'TESTRFID02'),
(273, 'EXIT', 'LPR_MISMAT', '2025-12-24 14:38:42', 'TESTRFID02'),
(274, 'EXIT', 'FACE_MISMA', '2025-12-24 14:39:00', 'TESTRFID02'),
(275, 'EXIT', 'FACE_MISMA', '2025-12-24 14:39:22', 'TESTRFID02'),
(276, 'EXIT', 'FACE_MISMA', '2025-12-24 14:45:08', 'TESTRFID02'),
(277, 'ENTRY', 'OPEN', '2025-12-24 14:45:34', 'TESTRFID02'),
(278, 'EXIT', 'OPEN', '2025-12-24 14:45:44', 'TESTRFID02'),
(279, 'ENTRY', 'OPEN', '2025-12-24 14:47:05', 'TESTRFID02'),
(280, 'EXIT', 'OPEN', '2025-12-24 14:47:27', 'TESTRFID02'),
(281, 'ENTRY', 'RFID_INVAL', '2025-12-25 10:36:19', 'D3E9FD13'),
(282, 'ENTRY', 'OPEN', '2025-12-25 10:39:33', 'D3E9FD13'),
(283, 'ENTRY', 'ALREADY_IN', '2025-12-25 11:29:28', 'D3E9FD13'),
(284, 'ENTRY', 'OPEN', '2025-12-26 15:11:13', '5E68200E'),
(285, 'ENTRY', 'LPR_FAIL', '2025-12-26 15:24:53', 'D3E9FD13'),
(286, 'ENTRY', 'FACE_FAIL', '2025-12-26 15:25:50', 'D3E9FD13'),
(287, 'ENTRY', 'FACE_FAIL', '2025-12-26 15:26:09', 'D3E9FD13'),
(288, 'ENTRY', 'OPEN', '2025-12-26 15:26:22', 'D3E9FD13'),
(289, 'ENTRY', 'FACE_FAIL', '2025-12-26 15:33:47', 'TESTRFID01'),
(290, 'ENTRY', 'OPEN', '2025-12-26 15:39:27', 'TESTRFID01'),
(291, 'ENTRY', 'PARKING_FU', '2025-12-26 15:43:57', 'TESTRFID01'),
(292, 'EXIT', 'NO_ACTIVE_', '2025-12-26 15:45:36', 'TESTRFID01'),
(293, 'EXIT', 'LPR_MISMAT', '2025-12-26 15:50:07', 'D3E9FD13'),
(294, 'EXIT', 'LPR_MISMAT', '2025-12-26 15:50:21', 'D3E9FD13'),
(295, 'ENTRY', 'ALREADY_IN', '2025-12-26 15:52:04', '5E68200E'),
(296, 'ENTRY', 'ALREADY_IN', '2025-12-26 15:53:04', '5E68200E'),
(297, 'EXIT', 'OPEN', '2025-12-26 15:53:30', '5E68200E'),
(298, 'EXIT', 'NO_ACTIVE_', '2025-12-26 15:55:32', '5E68200E'),
(299, 'EXIT', 'FACE_MISMA', '2025-12-26 15:56:37', 'D3E9FD13'),
(300, 'ENTRY', 'OPEN', '2026-03-17 11:58:00', '5E68200E'),
(301, 'ENTRY', 'ALREADY_IN', '2026-03-17 12:26:38', '5E68200E'),
(302, 'ENTRY', 'OPEN', '2026-03-17 12:28:03', '5E68200E'),
(303, 'ENTRY', 'OPEN', '2026-03-17 13:22:14', '5E68200E'),
(304, 'EXIT', 'NO_ACTIVE_', '2026-03-17 13:42:42', '5E68200E'),
(305, 'ENTRY', 'OPEN', '2026-03-17 13:42:58', '5E68200E'),
(306, 'ENTRY', 'ALREADY_IN', '2026-03-17 13:44:55', '5E68200E'),
(307, 'EXIT', 'LPR_MISMAT', '2026-03-17 13:50:15', '5E68200E'),
(308, 'EXIT', 'LPR_MISMAT', '2026-03-17 13:50:35', '5E68200E'),
(309, 'EXIT', 'NO_ACTIVE_', '2026-03-17 13:52:28', '5E68200E'),
(310, 'EXIT', 'NO_ACTIVE_', '2026-03-17 13:52:39', '5E68200E'),
(311, 'ENTRY', 'OPEN', '2026-03-17 13:53:16', '5E68200E'),
(312, 'EXIT', 'NO_ACTIVE_', '2026-03-17 14:53:47', '5E68200E'),
(313, 'ENTRY', 'OPEN', '2026-03-17 14:53:58', '5E68200E'),
(314, 'ENTRY', 'OPEN', '2026-03-17 14:55:53', 'TESTRFID02'),
(315, 'EXIT', 'LPR_MISMAT', '2026-03-17 14:57:21', '5E68200E'),
(316, 'EXIT', 'FACE_MISMA', '2026-03-17 14:57:49', '5E68200E'),
(317, 'EXIT', 'FACE_MISMA', '2026-03-17 14:58:05', '5E68200E'),
(318, 'EXIT', 'FACE_MISMA', '2026-03-17 14:58:58', '5E68200E'),
(319, 'EXIT', 'FACE_MISMA', '2026-03-17 14:59:34', '5E68200E'),
(320, 'EXIT', 'FACE_MISMA', '2026-03-17 15:00:22', '5E68200E');

-- --------------------------------------------------------

--
-- Table structure for table `information`
--

CREATE TABLE `information` (
  `Email` text NOT NULL,
  `Password` text NOT NULL,
  `Name` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `DateOfBirth` date NOT NULL,
  `Address` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `information`
--

INSERT INTO `information` (`Email`, `Password`, `Name`, `DateOfBirth`, `Address`) VALUES
('vinh.phan@eiu.edu.vn', '123456', 'Vinh', '2018-10-10', 'Binh Duong'),
('khang.vo.k3set@eiu.edu.vn', '123456', 'duykhang', '1995-01-29', 'Binh Duong'),
('thanh.tran.k2000@gmail.com', '123456', 'Thanh', '1994-09-27', 'BD-BB'),
('pvvinhbk@gmail.com', 'abc@123', 'Vinh Phan', '1984-12-08', 'Phu Hoa, TDM, BD');

-- --------------------------------------------------------

--
-- Table structure for table `parkinghistory`
--

CREATE TABLE `parkinghistory` (
  `HistoryID` bigint(20) NOT NULL,
  `RFID` varchar(20) DEFAULT NULL,
  `SlotID` int(11) DEFAULT NULL,
  `TimeIn` datetime DEFAULT NULL,
  `TimeOut` datetime DEFAULT NULL,
  `Duration` int(11) DEFAULT NULL,
  `Fee` decimal(10,2) DEFAULT NULL,
  `ImageFullEntry` varchar(255) DEFAULT NULL,
  `PlateNumberEntry` varchar(32) DEFAULT NULL,
  `FaceImageEntry` varchar(255) DEFAULT NULL,
  `ImageFullExit` varchar(255) DEFAULT NULL,
  `PlateNumberExit` varchar(32) DEFAULT NULL,
  `FaceImageExit` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `parkinghistory`
--

INSERT INTO `parkinghistory` (`HistoryID`, `RFID`, `SlotID`, `TimeIn`, `TimeOut`, `Duration`, `Fee`, `ImageFullEntry`, `PlateNumberEntry`, `FaceImageEntry`, `ImageFullExit`, `PlateNumberExit`, `FaceImageExit`) VALUES
(2, '90172383', 1, '2025-08-18 15:52:34', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(10, 'TESTRFID01', NULL, '2025-12-19 12:55:42', '2025-12-19 13:22:38', 26, 260.00, '../smart_parking_data/full_crop_LP\\29C1-99999_1766123742.jpg', '29C1-99999', NULL, '../smart_parking_data/full_crop_LP\\29C1-99999_1766125358.jpg', '29C1-99999', NULL),
(11, 'TESTRFID01', NULL, '2025-12-19 13:24:14', '2025-12-19 13:43:23', 19, 190.00, '../smart_parking_data/full_crop_LP\\12B1-16888_1766125453.jpg', '12B1-16888', NULL, '../smart_parking_data/full_crop_LP\\12B1-16888_1766126603.jpg', '12B1-16888', NULL),
(12, 'TESTRFID01', 1, '2025-12-19 13:44:24', '2025-12-19 13:52:36', 8, 80.00, '../smart_parking_data/full_crop_LP\\29C1-99999_1766126663.jpg', '29C1-99999', NULL, '../smart_parking_data/full_crop_LP\\29C1-99999_1766127155.jpg', '29C1-99999', NULL),
(13, 'TESTRFID01', 1, '2025-12-19 15:38:21', '2025-12-19 15:43:29', 5, 50.00, '../smart_parking_data/full_crop_LP\\98B3-33333_1766133493.jpg', '98B3-33333', 'D:\\Project1\\License-Plate-Recognition\\License-Plate-Recognition\\database\\face_20251219_153821.jpg', '../smart_parking_data/full_crop_LP\\98B3-33333_1766133633.jpg', '98B3-33333', 'D:\\Project1\\License-Plate-Recognition\\License-Plate-Recognition\\database\\face_20251219_153821.jpg'),
(14, 'TESTRFID01', 1, '2025-12-19 15:55:17', '2025-12-19 16:02:09', 6, 60.00, '../smart_parking_data/full_crop_LP\\98B3-33333_1766134509.jpg', '98B3-33333', 'database\\face_20251219_155516.jpg', '../smart_parking_data/full_crop_LP\\98B3-33333_1766134920.jpg', '98B3-33333', 'database\\face_20251219_155516.jpg'),
(15, 'TESTRFID01', 1, '2025-12-19 16:08:41', '2025-12-19 16:27:17', 18, 180.00, '../smart_parking_data/full_crop_LP\\98B3-33333_1766135314.jpg', '98B3-33333', 'database\\face_20251219_160841.jpg', '../smart_parking_data/full_crop_LP\\98B3-33333_1766136426.jpg', '98B3-33333', 'database\\face_20251219_155516.jpg'),
(16, 'TESTRFID01', 1, '2025-12-19 16:36:59', '2025-12-19 16:48:23', 11, 110.00, '../smart_parking_data/full_crop_LP\\20H1-66666_1766137009.jpg', '20H1-66666', 'database\\face_20251219_163659.jpg', '../smart_parking_data/full_crop_LP\\20H1-66666_1766137695.jpg', '20H1-66666', 'database\\face_20251219_155516.jpg'),
(17, 'TESTRFID01', 1, '2025-12-19 17:01:36', '2025-12-19 17:14:10', 12, 120.00, '../smart_parking_data/full_crop_LP\\20H1-66666_1766138489.jpg', '20H1-66666', 'database\\face_20251219_170136.jpg', '../smart_parking_data/full_crop_LP\\20H1-66666_1766139242.jpg', '20H1-66666', 'database\\face_20251219_170136.jpg'),
(18, 'TESTRFID01', 1, '2025-12-19 17:15:10', '2025-12-22 13:01:09', 4065, 40650.00, '../smart_parking_data/full_crop_LP\\20H1-66666_1766139305.jpg', '20H1-66666', 'database\\face_20251219_171510.jpg', '../smart_parking_data/full_crop_LP\\20H1-66666_1766383259.jpg', '20H1-66666', 'database\\face_20251222_122937.jpg'),
(21, 'TESTRFID01', NULL, '2025-12-22 13:40:35', '2025-12-22 13:43:36', 3, 30.00, '../smart_parking_data/full_crop_LP\\20H1-66666_1766385631.jpg', '20H1-66666', 'database\\face_20251222_134035.jpg', '../smart_parking_data/full_crop_LP\\20H1-66666_1766385811.jpg', '20H1-66666', 'database\\face_20251222_134035.jpg'),
(30, '5E68200E', NULL, '2025-12-22 16:14:25', '2025-12-22 16:38:10', 23, 230.00, '../smart_parking_data/full_crop_LP\\59V1-79379_1766394861.jpg', '59V1-79379', 'database\\face_20251222_161425.jpg', '../smart_parking_data/full_crop_LP\\59V1-79379_1766396278.jpg', '59V1-79379', 'database\\face_20251222_155903.jpg'),
(31, '5E68200E', NULL, '2025-12-22 16:40:55', '2025-12-22 16:44:55', 4, 40.00, '../smart_parking_data/full_crop_LP\\59V1-79379_1766396450.jpg', '59V1-79379', 'database\\face_20251222_164054.jpg', '../smart_parking_data/full_crop_LP\\59V1-79379_1766396684.jpg', '59V1-79379', 'database\\face_20251222_161326.jpg'),
(32, '5E68200E', 1, '2025-12-22 16:46:52', '2025-12-22 17:02:58', 16, 160.00, '../smart_parking_data/full_crop_LP\\59V1-79379_1766396808.jpg', '59V1-79379', 'database\\face_20251222_164651.jpg', '../smart_parking_data/full_crop_LP\\59V1-79379_1766397767.jpg', '59V1-79379', 'database\\face_20251219_160841.jpg'),
(33, '5E68200E', NULL, '2025-12-22 17:03:31', '2025-12-22 17:04:02', 0, 0.00, '../smart_parking_data/full_crop_LP\\29C1-99999_1766397807.jpg', '29C1-99999', 'database\\face_20251222_170331.jpg', '../smart_parking_data/full_crop_LP\\29C1-99999_1766397833.jpg', '29C1-99999', 'database\\face_20251222_164054.jpg'),
(34, '5E68200E', NULL, '2025-12-22 17:07:36', '2025-12-22 17:08:05', 0, 0.00, '../smart_parking_data/full_crop_LP\\29C1-99999_1766398051.jpg', '29C1-99999', 'database\\face_20251222_170735.jpg', '../smart_parking_data/full_crop_LP\\29C1-99999_1766398074.jpg', '29C1-99999', 'database\\face_20251222_141340.jpg'),
(35, '5E68200E', NULL, '2025-12-22 17:08:27', '2025-12-22 17:12:22', 3, 30.00, '../smart_parking_data/full_crop_LP\\29C1-99999_1766398103.jpg', '29C1-99999', 'database\\face_20251222_170827.jpg', '../smart_parking_data/full_crop_LP\\29C1-99999_1766398330.jpg', '29C1-99999', 'database\\face_20251219_160841.jpg'),
(36, '5E68200E', NULL, '2025-12-22 17:12:42', '2025-12-22 17:13:09', 0, 0.00, '../smart_parking_data/full_crop_LP\\29C1-99999_1766398358.jpg', '29C1-99999', 'database\\face_20251222_171242.jpg', '../smart_parking_data/full_crop_LP\\29C1-99999_1766398379.jpg', '29C1-99999', 'database\\face_20251219_163659.jpg'),
(37, '5E68200E', NULL, '2025-12-22 17:16:25', '2025-12-22 17:21:27', 5, 50.00, '../smart_parking_data/full_crop_LP\\12B1-1688_1766398580.jpg', '12B1-16888', 'database\\face_20251222_171625.jpg', '../smart_parking_data/full_crop_LP\\12B1-16888_1766398876.jpg', '12B1-16888', 'database\\face_20251219_160841.jpg'),
(38, '5E68200E', NULL, '2025-12-22 17:21:50', '2025-12-22 17:22:23', 0, 0.00, '../smart_parking_data/full_crop_LP\\12B1-16888_1766398906.jpg', '12B1-16888', 'database\\face_20251222_172149.jpg', '../smart_parking_data/full_crop_LP\\12B1-16888_1766398935.jpg', '12B1-16888', 'database\\face_20251219_163659.jpg'),
(39, '5E68200E', NULL, '2025-12-22 17:22:44', '2025-12-22 17:23:09', 0, 0.00, '../smart_parking_data/full_crop_LP\\12B1-16888_1766398962.jpg', '12B1-16888', 'database\\face_20251222_172244.jpg', '../smart_parking_data/full_crop_LP\\12B1-16888_1766398980.jpg', '12B1-16888', 'database\\face_20251222_164651.jpg'),
(40, '5E68200E', NULL, '2025-12-22 17:23:31', '2025-12-22 17:23:54', 0, 0.00, '../smart_parking_data/full_crop_LP\\12B1-16888_1766399008.jpg', '12B1-16888', 'database\\face_20251222_172330.jpg', '../smart_parking_data/full_crop_LP\\12B1-16888_1766399025.jpg', '12B1-16888', 'database\\face_20251222_170331.jpg'),
(41, '5E68200E', NULL, '2025-12-22 17:24:10', '2025-12-22 17:24:28', 0, 0.00, '../smart_parking_data/full_crop_LP\\12B1-16888_1766399048.jpg', '12B1-16888', 'database\\face_20251222_172410.jpg', '../smart_parking_data/full_crop_LP\\12B1-16888_1766399059.jpg', '12B1-16888', 'database\\face_20251222_164054.jpg'),
(42, '5E68200E', NULL, '2025-12-23 13:31:25', '2025-12-23 13:44:13', 12, 120.00, '../smart_parking_data/full_crop_LP\\611-82234_1766471482.jpg', '611-82234', 'database\\face_20251223_133125.jpg', '../smart_parking_data/full_crop_LP\\611-82234_1766472243.jpg', '611-82234', 'database\\face_20251219_155516.jpg'),
(43, '5E68200E', NULL, '2025-12-23 13:44:28', '2025-12-23 13:45:11', 0, 0.00, '../smart_parking_data/full_crop_LP\\611-82234_1766472268.jpg', '611-82234', 'database\\face_20251223_134428.jpg', '../smart_parking_data/full_crop_LP\\611-82234_1766472304.jpg', '611-82234', 'database\\face_20251219_155516.jpg'),
(44, '5E68200E', NULL, '2025-12-23 13:45:38', '2025-12-23 13:46:00', 0, 0.00, '../smart_parking_data/full_crop_LP\\59H1-36399_1766472337.jpg', '59H1-36399', 'database\\face_20251223_134538.jpg', '../smart_parking_data/full_crop_LP\\59H1-36399_1766472352.jpg', '59H1-36399', 'database\\face_20251219_163659.jpg'),
(45, '5E68200E', NULL, '2025-12-23 13:46:23', '2025-12-23 13:46:48', 0, 0.00, '../smart_parking_data/full_crop_LP\\59H1-36399_1766472382.jpg', '59H1-36399', 'database\\face_20251223_134623.jpg', '../smart_parking_data/full_crop_LP\\59H1-36399_1766472401.jpg', '59H1-36399', 'database\\face_20251219_155516.jpg'),
(46, '5E68200E', NULL, '2025-12-23 13:47:14', '2025-12-23 13:47:42', 0, 0.00, '../smart_parking_data/full_crop_LP\\59H1-36399_1766472432.jpg', '59H1-36399', 'database\\face_20251223_134714.jpg', '../smart_parking_data/full_crop_LP\\59H1-36399_1766472454.jpg', '59H1-36399', 'database\\face_20251222_121902.jpg'),
(47, '5E68200E', NULL, '2025-12-23 13:54:01', '2025-12-23 13:54:34', 0, 0.00, '../smart_parking_data/full_crop_LP\\59H1-36399_1766472839.jpg', '59H1-36399', 'database\\face_20251223_135401.jpg', '../smart_parking_data/full_crop_LP\\59H1-36399_1766472864.jpg', '59H1-36399', 'database\\face_20251222_171242.jpg'),
(48, '5E68200E', NULL, '2025-12-23 13:58:06', '2025-12-23 13:58:42', 0, 0.00, '../smart_parking_data/full_crop_LP\\59H1-36399_1766473085.jpg', '59H1-36399', 'database\\face_20251223_135806.jpg', '../smart_parking_data/full_crop_LP\\59H1-36399_1766473112.jpg', '59H1-36399', 'database\\face_exit_20251223_135842.jpg'),
(49, '5E68200E', NULL, '2025-12-23 14:02:47', '2025-12-23 14:03:13', 0, 0.00, '../smart_parking_data/full_crop_LP\\59H1-36399_1766473365.jpg', '59H1-36399', 'database\\face_20251223_140247.jpg', '../smart_parking_data/full_crop_LP\\59H1-36399_1766473381.jpg', '59H1-36399', 'database\\face_exit_20251223_140312.jpg'),
(52, 'TESTRFID02', 1, '2025-12-23 14:59:54', '2025-12-23 15:10:54', 11, 110.00, '../smart_parking_data/full_crop_LP\\51F97022_23122025_145953.jpg', '51F97022', 'database\\face_20251223_145954.jpg', '../smart_parking_data/full_crop_LP\\51F97022_23122025_151042.jpg', '51F97022', 'database\\face_exit_20251223_151054.jpg'),
(54, 'TESTRFID02', NULL, '2025-12-23 15:22:35', '2025-12-23 15:23:05', 0, 0.00, '../smart_parking_data/full_crop_LP\\51F97022_23122025_152234.jpg', '51F97022', 'database\\face_20251223_152235.jpg', '../smart_parking_data/full_crop_LP\\51F97022_23122025_152302.jpg', '51F97022', 'database\\face_exit_20251223_152305.jpg'),
(55, 'TESTRFID03', 1, '2025-12-23 15:23:33', '2025-12-23 15:25:05', 1, 10.00, '../smart_parking_data/full_crop_LP\\51F97022_23122025_152332.jpg', '51F97022', 'database\\face_20251223_152333.jpg', '../smart_parking_data/full_crop_LP\\51F97022_23122025_152504.jpg', '51F97022', 'database\\face_exit_20251223_152505.jpg'),
(56, 'TESTRFID03', NULL, '2025-12-23 15:25:20', '2025-12-23 15:25:39', 0, 0.00, '../smart_parking_data/full_crop_LP\\51F97022_23122025_152519.jpg', '51F97022', 'database\\face_20251223_152520.jpg', '../smart_parking_data/full_crop_LP\\51F97022_23122025_152535.jpg', '51F97022', 'database\\face_exit_20251223_152539.jpg'),
(57, 'TESTRFID03', NULL, '2025-12-23 15:29:39', '2025-12-23 15:29:59', 0, 0.00, '../smart_parking_data/full_crop_LP\\51F97022_23122025_152935.jpg', '51F97022', 'database\\face_20251223_152939.jpg', '../smart_parking_data/full_crop_LP\\51F97022_23122025_152956.jpg', '51F97022', 'database\\face_exit_20251223_152959.jpg'),
(58, 'TESTRFID03', 1, '2025-12-23 15:34:08', '2025-12-23 15:35:29', 1, 10.00, '../smart_parking_data/full_crop_LP\\51F97022_23122025_153406.jpg', '51F97022', 'database\\face_20251223_153408.jpg', '../smart_parking_data/full_crop_LP\\51F97022_23122025_153526.jpg', '51F97022', 'database\\face_exit_20251223_153529.jpg'),
(59, 'TESTRFID03', NULL, '2025-12-23 15:35:43', '2025-12-23 15:41:31', 5, 50.00, '../smart_parking_data/full_crop_LP\\51F97022_23122025_153542.jpg', '51F97022', 'database\\face_20251223_153543.jpg', '../smart_parking_data/full_crop_LP\\51F97022_23122025_154128.jpg', '51F97022', 'database\\face_exit_20251223_154131.jpg'),
(60, 'TESTRFID03', NULL, '2025-12-23 15:41:42', '2025-12-23 15:42:14', 0, 0.00, '../smart_parking_data/full_crop_LP\\51F97022_23122025_154141.jpg', '51F97022', 'database\\face_20251223_154142.jpg', '../smart_parking_data/full_crop_LP\\51F97022_23122025_154209.jpg', '51F97022', 'database\\face_exit_20251223_154214.jpg'),
(61, 'TESTRFID03', NULL, '2025-12-23 15:43:05', '2025-12-23 15:44:22', 1, 10.00, '../smart_parking_data/full_crop_LP\\51F97022_23122025_154304.jpg', '51F97022', 'database\\face_20251223_154305.jpg', '../smart_parking_data/full_crop_LP\\51F97022_23122025_154416.jpg', '51F97022', 'database\\face_exit_20251223_154422.jpg'),
(62, 'TESTRFID03', 1, '2025-12-23 15:44:47', NULL, NULL, NULL, '../smart_parking_data/full_crop_LP\\51F97022_23122025_154445.jpg', '51F97022', 'database\\face_20251223_154447.jpg', NULL, NULL, NULL),
(66, 'TESTRFID02', NULL, '2025-12-23 16:35:20', '2025-12-23 16:35:42', 0, 0.00, '../smart_parking_data/full_crop_LP\\51G-74372_23122025_163518.jpg', '51G-74372', 'database\\face_20251223_163520.jpg', '../smart_parking_data/full_crop_LP\\51G-74372_23122025_163536.jpg', '51G-74372', 'database\\face_exit_20251223_163542.jpg'),
(70, 'TESTRFID02', NULL, '2025-12-24 14:45:34', '2025-12-24 14:45:44', 0, 0.00, '../smart_parking_data/full_crop_LP\\99E1-22268_24122025_144533.jpg', '99E1-22268', '../smart_parking_data/face_img\\face_20251224_144534.jpg', '../smart_parking_data/full_crop_LP\\99E1-22268_24122025_144543.jpg', '99E1-22268', '../smart_parking_data/face_img\\face_exit_20251224_144544.jpg'),
(71, 'TESTRFID02', NULL, '2025-12-24 14:47:05', '2025-12-24 14:47:27', 0, 0.00, '../smart_parking_data/full_crop_LP\\99E1-22268_24122025_144700.jpg', '99E1-22268', '../smart_parking_data/face_img\\face_20251224_144705.jpg', '../smart_parking_data/full_crop_LP\\99E1-22268_24122025_144724.jpg', '99E1-22268', '../smart_parking_data/face_img\\face_exit_20251224_144727.jpg'),
(79, '5E68200E', 1, '2026-03-17 13:42:58', '2026-03-17 13:45:11', 2, 2.00, '../smart_parking_data/full_crop_LP\\59H1-36399_17032026_134256.jpg', '59H1-36399', '../smart_parking_data/face_img\\face_20260317_134258.jpg', '../smart_parking_data/full_crop_LP\\59H1-36399_17032026_134507.jpg', '59H1-36399', '../smart_parking_data/face_img\\face_exit_20260317_134510.jpg'),
(81, '5E68200E', 1, '2026-03-17 14:53:58', NULL, NULL, NULL, '../smart_parking_data/full_crop_LP\\59H1-36399_17032026_145357.jpg', '59H1-36399', '../smart_parking_data/face_img\\face_20260317_145358.jpg', '../smart_parking_data/full_crop_LP\\59H1-36399_17032026_162922.jpg', '59H1-36399', '../smart_parking_data/face_img\\face_exit_20260317_162925.jpg'),
(82, 'TESTRFID02', 6, '2026-03-17 14:55:53', '2026-03-17 15:27:36', 31, 5000.00, '../smart_parking_data/full_crop_LP\\99E1-22268_17032026_145552.jpg', '99E1-22268', '../smart_parking_data/face_img\\face_20260317_145553.jpg', '../smart_parking_data/full_crop_LP\\99E1-22268_17032026_152444.jpg', '99E1-22268', '../smart_parking_data/face_img\\face_exit_20260317_152445.jpg');

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
(1, '1', 'A', 0, NULL, 1, 4, NULL),
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

-- --------------------------------------------------------

--
-- Table structure for table `payments`
--

CREATE TABLE `payments` (
  `PaymentID` int(11) NOT NULL,
  `RFID` varchar(50) DEFAULT NULL,
  `HistoryID` int(11) DEFAULT NULL,
  `Amount` int(11) DEFAULT NULL,
  `Status` enum('pending','waiting','paid') DEFAULT 'pending',
  `CreatedAt` timestamp NOT NULL DEFAULT current_timestamp(),
  `Notified` tinyint(4) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `payments`
--

INSERT INTO `payments` (`PaymentID`, `RFID`, `HistoryID`, `Amount`, `Status`, `CreatedAt`, `Notified`) VALUES
(1, 'TESTRFID02', 76, 10, 'paid', '2026-03-16 08:06:41', 1),
(2, 'TESTRFID03', 62, 1194830, 'paid', '2026-03-16 08:08:02', 1),
(3, 'TESTRFID03', 77, 0, 'paid', '2026-03-16 08:15:16', 1),
(4, 'TESTRFID03', 78, 2000, 'paid', '2026-03-16 08:20:37', 1),
(5, 'TESTRFID03', 79, 0, 'paid', '2026-03-16 08:47:33', 1),
(6, 'TESTRFID03', 80, 20, 'paid', '2026-03-16 09:19:21', 1),
(7, '5E68200E', 78, 5000, 'paid', '2026-03-17 06:26:21', 1),
(8, '5E68200E', 80, 0, 'paid', '2026-03-17 06:53:35', 1),
(9, '5E68200E', 81, 5000, 'paid', '2026-03-17 08:04:22', 1),
(10, 'TESTRFID02', 82, 5000, 'paid', '2026-03-17 08:24:45', 1),
(11, '5E68200E', 81, 10000, 'paid', '2026-03-17 09:29:25', 0);

-- --------------------------------------------------------

--
-- Table structure for table `rfidcard`
--

CREATE TABLE `rfidcard` (
  `RFID` varchar(20) NOT NULL,
  `OwnerName` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `VehiclePlate` varchar(15) DEFAULT NULL,
  `PhoneNumber` varchar(15) DEFAULT NULL,
  `Type` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `rfidcard`
--

INSERT INTO `rfidcard` (`RFID`, `OwnerName`, `VehiclePlate`, `PhoneNumber`, `Type`) VALUES
('5E68200E', 'Phạm Nguyễn Bảo Trang', '61K - 7813129', '0665526556', 'SUV'),
('90172383', 'Trương Thị Vân', '93A - 779312', '0125545167', 'Basic'),
('D3E9FD13', 'T', 'WEWRW51', '2413654123', 'BMW'),
('TESTRFID01', 'Test User', '29T8-2843', '0123456789', 'Test'),
('TESTRFID02', 't2', '24FF786', '234562346', 'Inova'),
('TESTRFID03', 'test3', 'WWWWWWW', '4567897543', 'BMW');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `gatelog`
--
ALTER TABLE `gatelog`
  ADD PRIMARY KEY (`LogID`);

--
-- Indexes for table `parkinghistory`
--
ALTER TABLE `parkinghistory`
  ADD PRIMARY KEY (`HistoryID`),
  ADD KEY `RFID` (`RFID`),
  ADD KEY `SlotID` (`SlotID`);

--
-- Indexes for table `parkingslot`
--
ALTER TABLE `parkingslot`
  ADD PRIMARY KEY (`SlotID`);

--
-- Indexes for table `payments`
--
ALTER TABLE `payments`
  ADD PRIMARY KEY (`PaymentID`);

--
-- Indexes for table `rfidcard`
--
ALTER TABLE `rfidcard`
  ADD PRIMARY KEY (`RFID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `gatelog`
--
ALTER TABLE `gatelog`
  MODIFY `LogID` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=321;

--
-- AUTO_INCREMENT for table `parkinghistory`
--
ALTER TABLE `parkinghistory`
  MODIFY `HistoryID` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=83;

--
-- AUTO_INCREMENT for table `parkingslot`
--
ALTER TABLE `parkingslot`
  MODIFY `SlotID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- AUTO_INCREMENT for table `payments`
--
ALTER TABLE `payments`
  MODIFY `PaymentID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `parkinghistory`
--
ALTER TABLE `parkinghistory`
  ADD CONSTRAINT `parkinghistory_ibfk_1` FOREIGN KEY (`RFID`) REFERENCES `rfidcard` (`RFID`),
  ADD CONSTRAINT `parkinghistory_ibfk_2` FOREIGN KEY (`SlotID`) REFERENCES `parkingslot` (`SlotID`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
