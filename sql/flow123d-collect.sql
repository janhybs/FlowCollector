-- phpMyAdmin SQL Dump
-- version 4.0.10deb1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Jul 23, 2015 at 11:59 AM
-- Server version: 5.6.19-0ubuntu0.14.04.1
-- PHP Version: 5.5.9-1ubuntu4.5

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `flow123d-collect`
--

-- --------------------------------------------------------

--
-- Table structure for table `condition`
--

CREATE TABLE IF NOT EXISTS `condition` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `branch` varchar(64) COLLATE utf8_czech_ci NOT NULL,
  `build` varchar(128) COLLATE utf8_czech_ci NOT NULL,
  `timer_resolution` double NOT NULL,
  `task_name` varchar(128) COLLATE utf8_czech_ci NOT NULL,
  `task_size` int(11) NOT NULL,
  `process_count` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci AUTO_INCREMENT=12 ;

--
-- Dumping data for table `condition`
--

INSERT INTO `condition` (`id`, `branch`, `build`, `timer_resolution`, `task_name`, `task_size`, `process_count`) VALUES
(11, 'master', 'Jun 18 2015, 11:05:14 flags: -g -O0 -Wall -Wno-unused-local-typedefs -std=c++11', 0.00004913, 'Test10 - Unsteady flow in 2D, Mixed Hybrid method', 942, 1);

-- --------------------------------------------------------

--
-- Table structure for table `measurement`
--

CREATE TABLE IF NOT EXISTS `measurement` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(64) COLLATE utf8_czech_ci NOT NULL,
  `value` varchar(64) COLLATE utf8_czech_ci NOT NULL,
  `structure` varchar(64) COLLATE utf8_czech_ci NOT NULL,
  `cond` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `structure` (`structure`),
  KEY `condition` (`cond`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci AUTO_INCREMENT=44 ;

--
-- Dumping data for table `measurement`
--

INSERT INTO `measurement` (`id`, `type`, `value`, `structure`, `cond`) VALUES
(4, 'call-count-sum', '1', 'Whole Program', 11),
(5, 'cumul-time-sum', '0.003012342', 'Whole Program', 11),
(6, 'call-count-sum', '1', 'HC run simulation', 11),
(7, 'cumul-time-sum', '0.001164235', 'HC run simulation', 11),
(8, 'call-count-sum', '3', 'Solving MH system', 11),
(9, 'cumul-time-sum', '0.001163942', 'Solving MH system', 11),
(10, 'call-count-sum', '3', 'full assembly', 11),
(11, 'cumul-time-sum', '0.00042287', 'full assembly', 11),
(12, 'call-count-sum', '3', 'postprocess', 11),
(13, 'cumul-time-sum', '0.000000008', 'postprocess', 11),
(14, 'call-count-sum', '3', 'PETSC linear solver', 11),
(15, 'cumul-time-sum', '0.000069415', 'PETSC linear solver', 11),
(16, 'call-count-sum', '24', 'PETSC linear iteration', 11),
(17, 'cumul-time-sum', '0.000069406', 'PETSC linear iteration', 11),
(18, 'call-count-sum', '3', 'Darcy output', 11),
(19, 'cumul-time-sum', '0.0003622', 'Darcy output', 11),
(20, 'call-count-sum', '3', 'Fill OutputData', 11),
(21, 'cumul-time-sum', '0.000217887', 'Fill OutputData', 11),
(22, 'call-count-sum', '3', 'write_time_frame', 11),
(23, 'cumul-time-sum', '0.000016454', 'write_time_frame', 11),
(24, 'call-count-sum', '1', 'HC constructor', 11),
(25, 'cumul-time-sum', '0.000324094', 'HC constructor', 11),
(26, 'call-count-sum', '1', 'Reading mesh - init_from_input', 11),
(27, 'cumul-time-sum', '0.000048478', 'Reading mesh - init_from_input', 11),
(28, 'call-count-sum', '1', 'MESH - setup topology', 11),
(29, 'cumul-time-sum', '0.000014348', 'MESH - setup topology', 11),
(30, 'call-count-sum', '1', 'GMSHReader - read mesh', 11),
(31, 'cumul-time-sum', '0.000029713', 'GMSHReader - read mesh', 11),
(32, 'call-count-sum', '1', 'Darcy constructor', 11),
(33, 'cumul-time-sum', '0.000275232', 'Darcy constructor', 11),
(34, 'call-count-sum', '1', 'preallocation', 11),
(35, 'cumul-time-sum', '0.000257312', 'preallocation', 11),
(36, 'call-count-sum', '1', 'PETSC PREALLOCATION', 11),
(37, 'cumul-time-sum', '0.00025666', 'PETSC PREALLOCATION', 11),
(38, 'call-count-sum', '1', 'data init', 11),
(39, 'cumul-time-sum', '0.000000429', 'data init', 11),
(40, 'call-count-sum', '1', 'prepare parallel', 11),
(41, 'cumul-time-sum', '0.000004432', 'prepare parallel', 11),
(42, 'call-count-sum', '1', 'prepare scatter', 11),
(43, 'cumul-time-sum', '0.00000132', 'prepare scatter', 11);

-- --------------------------------------------------------

--
-- Table structure for table `structure`
--

CREATE TABLE IF NOT EXISTS `structure` (
  `name` varchar(64) COLLATE utf8_czech_ci NOT NULL,
  `parent` varchar(64) COLLATE utf8_czech_ci DEFAULT NULL,
  PRIMARY KEY (`name`),
  KEY `parent` (`parent`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;

--
-- Dumping data for table `structure`
--

INSERT INTO `structure` (`name`, `parent`) VALUES
('Whole Program', NULL),
('data init', 'Darcy constructor'),
('preallocation', 'Darcy constructor'),
('prepare parallel', 'Darcy constructor'),
('prepare scatter', 'Darcy constructor'),
('Fill OutputData', 'Darcy output'),
('write_time_frame', 'Darcy output'),
('Darcy constructor', 'HC constructor'),
('Reading mesh - init_from_input', 'HC constructor'),
('Solving MH system', 'HC run simulation'),
('PETSC linear iteration', 'PETSC linear solver'),
('PETSC PREALLOCATION', 'preallocation'),
('GMSHReader - read mesh', 'Reading mesh - init_from_input'),
('MESH - setup topology', 'Reading mesh - init_from_input'),
('Darcy output', 'Solving MH system'),
('full assembly', 'Solving MH system'),
('PETSC linear solver', 'Solving MH system'),
('postprocess', 'Solving MH system'),
('HC constructor', 'Whole Program'),
('HC run simulation', 'Whole Program');

--
-- Constraints for dumped tables
--

--
-- Constraints for table `measurement`
--
ALTER TABLE `measurement`
  ADD CONSTRAINT `measurement_ibfk_2` FOREIGN KEY (`cond`) REFERENCES `condition` (`id`),
  ADD CONSTRAINT `measurement_ibfk_1` FOREIGN KEY (`structure`) REFERENCES `structure` (`name`);

--
-- Constraints for table `structure`
--
ALTER TABLE `structure`
  ADD CONSTRAINT `structure_ibfk_1` FOREIGN KEY (`parent`) REFERENCES `structure` (`name`) ON DELETE CASCADE ON UPDATE CASCADE;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
