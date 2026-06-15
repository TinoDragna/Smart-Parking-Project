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
-- Cấu trúc bảng cho bảng `parkinghistory`
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Đang đổ dữ liệu cho bảng `parkinghistory`
--

INSERT INTO `parkinghistory` (`HistoryID`, `RFID`, `SlotID`, `TimeIn`, `TimeOut`, `Duration`, `Fee`, `ImageFullEntry`, `PlateNumberEntry`, `FaceImageEntry`, `ImageFullExit`, `PlateNumberExit`, `FaceImageExit`) VALUES
(13, 'TESTRFID01', 1, '2025-12-19 15:38:21', '2025-12-19 15:43:29', 5, '50.00', '../smart_parking_data/full_crop_LP\\98B3-33333_1766133493.jpg', '98B3-33333', 'database\\face_20251219_153821.jpg', '../smart_parking_data/full_crop_LP\\98B3-33333_1766133633.jpg', '98B3-33333', 'database\\face_20251219_153821.jpg'),
(14, 'TESTRFID01', 1, '2025-12-19 15:55:17', '2025-12-19 16:02:09', 6, '60.00', '../smart_parking_data/full_crop_LP\\98B3-33333_1766134509.jpg', '98B3-33333', 'database\\face_20251219_155516.jpg', '../smart_parking_data/full_crop_LP\\98B3-33333_1766134920.jpg', '98B3-33333', 'database\\face_20251219_155516.jpg'),
(15, 'TESTRFID01', 1, '2025-12-19 16:08:41', '2025-12-19 16:27:17', 18, '180.00', '../smart_parking_data/full_crop_LP\\98B3-33333_1766135314.jpg', '98B3-33333', 'database\\face_20251219_160841.jpg', '../smart_parking_data/full_crop_LP\\98B3-33333_1766136426.jpg', '98B3-33333', 'database\\face_20251219_155516.jpg'),
(16, 'TESTRFID01', 1, '2025-12-19 16:36:59', '2025-12-19 16:48:23', 11, '110.00', '../smart_parking_data/full_crop_LP\\20H1-66666_1766137009.jpg', '20H1-66666', 'database\\face_20251219_163659.jpg', '../smart_parking_data/full_crop_LP\\20H1-66666_1766137695.jpg', '20H1-66666', 'database\\face_20251219_155516.jpg'),
(17, 'TESTRFID01', 1, '2025-12-19 17:01:36', '2025-12-19 17:14:10', 12, '120.00', '../smart_parking_data/full_crop_LP\\20H1-66666_1766138489.jpg', '20H1-66666', 'database\\face_20251219_170136.jpg', '../smart_parking_data/full_crop_LP\\20H1-66666_1766139242.jpg', '20H1-66666', 'database\\face_20251219_170136.jpg'),
(18, 'TESTRFID01', 1, '2025-12-19 17:15:10', '2025-12-22 13:01:09', 4065, '40650.00', '../smart_parking_data/full_crop_LP\\20H1-66666_1766139305.jpg', '20H1-66666', 'database\\face_20251219_171510.jpg', '../smart_parking_data/full_crop_LP\\20H1-66666_1766383259.jpg', '20H1-66666', 'database\\face_20251222_122937.jpg'),
(21, 'TESTRFID01', 1, '2025-12-22 13:40:35', '2025-12-22 13:43:36', 3, '30.00', '../smart_parking_data/full_crop_LP\\20H1-66666_1766385631.jpg', '20H1-66666', 'database\\face_20251222_134035.jpg', '../smart_parking_data/full_crop_LP\\20H1-66666_1766385811.jpg', '20H1-66666', 'database\\face_20251222_134035.jpg'),
(30, '5E68200E', 1, '2025-12-22 16:14:25', '2025-12-22 16:38:10', 23, '230.00', '../smart_parking_data/full_crop_LP\\59V1-79379_1766394861.jpg', '59V1-79379', 'database\\face_20251222_161425.jpg', '../smart_parking_data/full_crop_LP\\59V1-79379_1766396278.jpg', '59V1-79379', 'database\\face_20251222_155903.jpg'),
(31, '5E68200E', 1, '2025-12-22 16:40:55', '2025-12-22 16:44:55', 4, '40.00', '../smart_parking_data/full_crop_LP\\59V1-79379_1766396450.jpg', '59V1-79379', 'database\\face_20251222_164054.jpg', '../smart_parking_data/full_crop_LP\\59V1-79379_1766396684.jpg', '59V1-79379', 'database\\face_20251222_161326.jpg'),
(32, '5E68200E', 1, '2025-12-22 16:46:52', '2025-12-22 17:02:58', 16, '160.00', '../smart_parking_data/full_crop_LP\\59V1-79379_1766396808.jpg', '59V1-79379', 'database\\face_20251222_164651.jpg', '../smart_parking_data/full_crop_LP\\59V1-79379_1766397767.jpg', '59V1-79379', 'database\\face_20251219_160841.jpg'),
(33, '5E68200E', 1, '2025-12-22 17:03:31', '2025-12-22 17:04:02', 0, '0.00', '../smart_parking_data/full_crop_LP\\29C1-99999_1766397807.jpg', '29C1-99999', 'database\\face_20251222_170331.jpg', '../smart_parking_data/full_crop_LP\\29C1-99999_1766397833.jpg', '29C1-99999', 'database\\face_20251222_164054.jpg'),
(34, '5E68200E', 1, '2025-12-22 17:07:36', '2025-12-22 17:08:05', 0, '0.00', '../smart_parking_data/full_crop_LP\\29C1-99999_1766398051.jpg', '29C1-99999', 'database\\face_20251222_170735.jpg', '../smart_parking_data/full_crop_LP\\29C1-99999_1766398074.jpg', '29C1-99999', 'database\\face_20251222_141340.jpg'),
(35, '5E68200E', 1, '2025-12-22 17:08:27', '2025-12-22 17:12:22', 3, '30.00', '../smart_parking_data/full_crop_LP\\29C1-99999_1766398103.jpg', '29C1-99999', 'database\\face_20251222_170827.jpg', '../smart_parking_data/full_crop_LP\\29C1-99999_1766398330.jpg', '29C1-99999', 'database\\face_20251219_160841.jpg'),
(36, '5E68200E', 1, '2025-12-22 17:12:42', '2025-12-22 17:13:09', 0, '0.00', '../smart_parking_data/full_crop_LP\\29C1-99999_1766398358.jpg', '29C1-99999', 'database\\face_20251222_171242.jpg', '../smart_parking_data/full_crop_LP\\29C1-99999_1766398379.jpg', '29C1-99999', 'database\\face_20251219_163659.jpg'),
(37, '5E68200E', 1, '2025-12-22 17:16:25', '2025-12-22 17:21:27', 5, '50.00', '../smart_parking_data/full_crop_LP\\12B1-1688_1766398580.jpg', '12B1-16888', 'database\\face_20251222_171625.jpg', '../smart_parking_data/full_crop_LP\\12B1-16888_1766398876.jpg', '12B1-16888', 'database\\face_20251219_160841.jpg'),
(38, '5E68200E', 1, '2025-12-22 17:21:50', '2025-12-22 17:22:23', 0, '0.00', '../smart_parking_data/full_crop_LP\\12B1-16888_1766398906.jpg', '12B1-16888', 'database\\face_20251222_172149.jpg', '../smart_parking_data/full_crop_LP\\12B1-16888_1766398935.jpg', '12B1-16888', 'database\\face_20251219_163659.jpg'),
(39, '5E68200E', 1, '2025-12-22 17:22:44', '2025-12-22 17:23:09', 0, '0.00', '../smart_parking_data/full_crop_LP\\12B1-16888_1766398962.jpg', '12B1-16888', 'database\\face_20251222_172244.jpg', '../smart_parking_data/full_crop_LP\\12B1-16888_1766398980.jpg', '12B1-16888', 'database\\face_20251222_164651.jpg'),
(40, '5E68200E', 1, '2025-12-22 17:23:31', '2025-12-22 17:23:54', 0, '0.00', '../smart_parking_data/full_crop_LP\\12B1-16888_1766399008.jpg', '12B1-16888', 'database\\face_20251222_172330.jpg', '../smart_parking_data/full_crop_LP\\12B1-16888_1766399025.jpg', '12B1-16888', 'database\\face_20251222_170331.jpg'),
(41, '5E68200E', 1, '2025-12-22 17:24:10', '2025-12-22 17:24:28', 0, '0.00', '../smart_parking_data/full_crop_LP\\12B1-16888_1766399048.jpg', '12B1-16888', 'database\\face_20251222_172410.jpg', '../smart_parking_data/full_crop_LP\\12B1-16888_1766399059.jpg', '12B1-16888', 'database\\face_20251222_164054.jpg'),
(42, '5E68200E', 1, '2025-12-23 13:31:25', '2025-12-23 13:44:13', 12, '120.00', '../smart_parking_data/full_crop_LP\\611-82234_1766471482.jpg', '611-82234', 'database\\face_20251223_133125.jpg', '../smart_parking_data/full_crop_LP\\611-82234_1766472243.jpg', '611-82234', 'database\\face_20251219_155516.jpg'),
(43, '5E68200E', 1, '2025-12-23 13:44:28', '2025-12-23 13:45:11', 0, '0.00', '../smart_parking_data/full_crop_LP\\611-82234_1766472268.jpg', '611-82234', 'database\\face_20251223_134428.jpg', '../smart_parking_data/full_crop_LP\\611-82234_1766472304.jpg', '611-82234', 'database\\face_20251219_155516.jpg'),
(44, '5E68200E', 1, '2025-12-23 13:45:38', '2025-12-23 13:46:00', 0, '0.00', '../smart_parking_data/full_crop_LP\\59H1-36399_1766472337.jpg', '59H1-36399', 'database\\face_20251223_134538.jpg', '../smart_parking_data/full_crop_LP\\59H1-36399_1766472352.jpg', '59H1-36399', 'database\\face_20251219_163659.jpg'),
(45, '5E68200E', 1, '2025-12-23 13:46:23', '2025-12-23 13:46:48', 0, '0.00', '../smart_parking_data/full_crop_LP\\59H1-36399_1766472382.jpg', '59H1-36399', 'database\\face_20251223_134623.jpg', '../smart_parking_data/full_crop_LP\\59H1-36399_1766472401.jpg', '59H1-36399', 'database\\face_20251219_155516.jpg'),
(46, '5E68200E', 1, '2025-12-23 13:47:14', '2025-12-23 13:47:42', 0, '0.00', '../smart_parking_data/full_crop_LP\\59H1-36399_1766472432.jpg', '59H1-36399', 'database\\face_20251223_134714.jpg', '../smart_parking_data/full_crop_LP\\59H1-36399_1766472454.jpg', '59H1-36399', 'database\\face_20251222_121902.jpg'),
(47, '5E68200E', 1, '2025-12-23 13:54:01', '2025-12-23 13:54:34', 0, '0.00', '../smart_parking_data/full_crop_LP\\59H1-36399_1766472839.jpg', '59H1-36399', 'database\\face_20251223_135401.jpg', '../smart_parking_data/full_crop_LP\\59H1-36399_1766472864.jpg', '59H1-36399', 'database\\face_20251222_171242.jpg'),
(48, '5E68200E', 1, '2025-12-23 13:58:06', '2025-12-23 13:58:42', 0, '0.00', '../smart_parking_data/full_crop_LP\\59H1-36399_1766473085.jpg', '59H1-36399', 'database\\face_20251223_135806.jpg', '../smart_parking_data/full_crop_LP\\59H1-36399_1766473112.jpg', '59H1-36399', 'database\\face_exit_20251223_135842.jpg'),
(49, '5E68200E', 1, '2025-12-23 14:02:47', '2025-12-23 14:03:13', 0, '0.00', '../smart_parking_data/full_crop_LP\\59H1-36399_1766473365.jpg', '59H1-36399', 'database\\face_20251223_140247.jpg', '../smart_parking_data/full_crop_LP\\59H1-36399_1766473381.jpg', '59H1-36399', 'database\\face_exit_20251223_140312.jpg'),
(52, 'TESTRFID02', 1, '2025-12-23 14:59:54', '2025-12-23 15:10:54', 11, '110.00', '../smart_parking_data/full_crop_LP\\51F97022_23122025_145953.jpg', '51F97022', 'database\\face_20251223_145954.jpg', '../smart_parking_data/full_crop_LP\\51F97022_23122025_151042.jpg', '51F97022', 'database\\face_exit_20251223_151054.jpg'),
(54, 'TESTRFID02', 1, '2025-12-23 15:22:35', '2025-12-23 15:23:05', 0, '0.00', '../smart_parking_data/full_crop_LP\\51F97022_23122025_152234.jpg', '51F97022', 'database\\face_20251223_152235.jpg', '../smart_parking_data/full_crop_LP\\51F97022_23122025_152302.jpg', '51F97022', 'database\\face_exit_20251223_152305.jpg'),
(55, 'TESTRFID03', 1, '2025-12-23 15:23:33', '2025-12-23 15:25:05', 1, '10.00', '../smart_parking_data/full_crop_LP\\51F97022_23122025_152332.jpg', '51F97022', 'database\\face_20251223_152333.jpg', '../smart_parking_data/full_crop_LP\\51F97022_23122025_152504.jpg', '51F97022', 'database\\face_exit_20251223_152505.jpg'),
(56, 'TESTRFID03', 1, '2025-12-23 15:25:20', '2025-12-23 15:25:39', 0, '0.00', '../smart_parking_data/full_crop_LP\\51F97022_23122025_152519.jpg', '51F97022', 'database\\face_20251223_152520.jpg', '../smart_parking_data/full_crop_LP\\51F97022_23122025_152535.jpg', '51F97022', 'database\\face_exit_20251223_152539.jpg'),
(57, 'TESTRFID03', 1, '2025-12-23 15:29:39', '2025-12-23 15:29:59', 0, '0.00', '../smart_parking_data/full_crop_LP\\51F97022_23122025_152935.jpg', '51F97022', 'database\\face_20251223_152939.jpg', '../smart_parking_data/full_crop_LP\\51F97022_23122025_152956.jpg', '51F97022', 'database\\face_exit_20251223_152959.jpg'),
(58, 'TESTRFID03', 1, '2025-12-23 15:34:08', '2025-12-23 15:35:29', 1, '10.00', '../smart_parking_data/full_crop_LP\\51F97022_23122025_153406.jpg', '51F97022', 'database\\face_20251223_153408.jpg', '../smart_parking_data/full_crop_LP\\51F97022_23122025_153526.jpg', '51F97022', 'database\\face_exit_20251223_153529.jpg'),
(59, 'TESTRFID03', 1, '2025-12-23 15:35:43', '2025-12-23 15:41:31', 5, '50.00', '../smart_parking_data/full_crop_LP\\51F97022_23122025_153542.jpg', '51F97022', 'database\\face_20251223_153543.jpg', '../smart_parking_data/full_crop_LP\\51F97022_23122025_154128.jpg', '51F97022', 'database\\face_exit_20251223_154131.jpg'),
(60, 'TESTRFID03', 1, '2025-12-23 15:41:42', '2025-12-23 15:42:14', 0, '0.00', '../smart_parking_data/full_crop_LP\\51F97022_23122025_154141.jpg', '51F97022', 'database\\face_20251223_154142.jpg', '../smart_parking_data/full_crop_LP\\51F97022_23122025_154209.jpg', '51F97022', 'database\\face_exit_20251223_154214.jpg'),
(61, 'TESTRFID03', 1, '2025-12-23 15:43:05', '2025-12-23 15:44:22', 1, '10.00', '../smart_parking_data/full_crop_LP\\51F97022_23122025_154304.jpg', '51F97022', 'database\\face_20251223_154305.jpg', '../smart_parking_data/full_crop_LP\\51F97022_23122025_154416.jpg', '51F97022', 'database\\face_exit_20251223_154422.jpg'),
(62, 'TESTRFID03', 6, '2025-12-23 15:44:47', NULL, NULL, NULL, '../smart_parking_data/full_crop_LP\\51F97022_23122025_154445.jpg', '51F97022', 'database\\face_20251223_154447.jpg', NULL, NULL, NULL),
(66, 'TESTRFID02', 1, '2025-12-23 16:35:20', '2025-12-23 16:35:42', 0, '0.00', '../smart_parking_data/full_crop_LP\\51G-74372_23122025_163518.jpg', '51G-74372', 'database\\face_20251223_163520.jpg', '../smart_parking_data/full_crop_LP\\51G-74372_23122025_163536.jpg', '51G-74372', 'database\\face_exit_20251223_163542.jpg'),
(70, 'TESTRFID02', 1, '2025-12-24 14:45:34', '2025-12-24 14:45:44', 0, '0.00', '../smart_parking_data/full_crop_LP\\99E1-22268_24122025_144533.jpg', '99E1-22268', '../smart_parking_data/face_img\\face_20251224_144534.jpg', '../smart_parking_data/full_crop_LP\\99E1-22268_24122025_144543.jpg', '99E1-22268', '../smart_parking_data/face_img\\face_exit_20251224_144544.jpg'),
(71, 'TESTRFID02', 1, '2025-12-24 14:47:05', '2025-12-24 14:47:27', 0, '0.00', '../smart_parking_data/full_crop_LP\\99E1-22268_24122025_144700.jpg', '99E1-22268', '../smart_parking_data/face_img\\face_20251224_144705.jpg', '../smart_parking_data/full_crop_LP\\99E1-22268_24122025_144724.jpg', '99E1-22268', '../smart_parking_data/face_img\\face_exit_20251224_144727.jpg'),
(73, '5E68200E', 1, '2025-12-26 15:11:13', '2025-12-26 15:53:30', 42, '420.00', '../smart_parking_data/full_crop_LP\\20A09999_26122025_151111.jpg', '20A09999', '../smart_parking_data/face_img\\face_20251226_151113.jpg', '../smart_parking_data/full_crop_LP\\20A09999_26122025_155325.jpg', '20A09999', '../smart_parking_data/face_img\\face_exit_20251226_155330.jpg'),
(74, 'D3E9FD13', 6, '2025-12-26 15:26:22', '2026-06-15 10:51:04', 245964, '99999999.99', '../smart_parking_data/full_crop_LP\\30G25678_26122025_152621.jpg', '30G25678', '../smart_parking_data/face_img\\face_20251226_152622.jpg', NULL, 'ADMIN_MANUAL', NULL),
(79, '5E68200E', 1, '2026-03-17 13:42:58', '2026-03-17 13:45:11', 2, '2.00', '../smart_parking_data/full_crop_LP\\59H1-36399_17032026_134256.jpg', '59H1-36399', '../smart_parking_data/face_img\\face_20260317_134258.jpg', '../smart_parking_data/full_crop_LP\\59H1-36399_17032026_134507.jpg', '59H1-36399', '../smart_parking_data/face_img\\face_exit_20260317_134510.jpg'),
(81, '5E68200E', 1, '2026-03-17 14:53:58', '2026-06-15 10:09:31', 129315, '64500000.00', '../smart_parking_data/full_crop_LP\\59H1-36399_17032026_145357.jpg', '59H1-36399', '../smart_parking_data/face_img\\face_20260317_145358.jpg', '../smart_parking_data/full_crop_LP\\59H1-36399_17032026_162922.jpg', 'ADMIN_MANUAL', '../smart_parking_data/face_img\\face_exit_20260317_162925.jpg'),
(82, 'TESTRFID02', 6, '2026-03-17 14:55:53', '2026-03-17 15:27:36', 31, '5000.00', '../smart_parking_data/full_crop_LP\\99E1-22268_17032026_145552.jpg', '99E1-22268', '../smart_parking_data/face_img\\face_20260317_145553.jpg', '../smart_parking_data/full_crop_LP\\99E1-22268_17032026_152444.jpg', '99E1-22268', '../smart_parking_data/face_img\\face_exit_20260317_152445.jpg'),
(83, 'TESTRFID01', 6, '2026-04-01 11:25:35', '2026-06-15 01:37:48', 107412, '53580000.00', '../smart_parking_data/full_crop_LP\\51F-97022_01042026_112535.jpg', '51F-97022', '../smart_parking_data/face_img\\face_20260401_112535.jpg', NULL, 'ADMIN_MANUAL', NULL),
(84, 'TESTRFID02', 1, '2026-04-01 14:02:15', '2026-04-01 14:03:51', 2, '30000.00', '../smart_parking_data/full_crop_LP\\60A99999_01042026_140210.jpg', '60A99999', '../smart_parking_data/face_img\\face_20260401_140215.jpg', '../smart_parking_data/full_crop_LP\\60A99999_01042026_140347.jpg', '60A99999', '../smart_parking_data/face_img\\face_exit_20260401_140350.jpg');

--
-- Chỉ mục cho các bảng đã đổ
--

--
-- Chỉ mục cho bảng `parkinghistory`
--
ALTER TABLE `parkinghistory`
  ADD PRIMARY KEY (`HistoryID`),
  ADD KEY `RFID` (`RFID`),
  ADD KEY `SlotID` (`SlotID`);

--
-- AUTO_INCREMENT cho các bảng đã đổ
--

--
-- AUTO_INCREMENT cho bảng `parkinghistory`
--
ALTER TABLE `parkinghistory`
  MODIFY `HistoryID` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=86;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
