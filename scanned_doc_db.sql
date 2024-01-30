-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server Version:               10.6.12-MariaDB-0ubuntu0.22.04.1 - Ubuntu 22.04
-- Server Betriebssystem:        debian-linux-gnu
-- HeidiSQL Version:             12.3.0.6589
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Exportiere Datenbank Struktur für scanned_doc_db
CREATE DATABASE IF NOT EXISTS `scanned_doc_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;
USE `scanned_doc_db`;

-- Exportiere Struktur von Tabelle scanned_doc_db.DocTag
CREATE TABLE IF NOT EXISTS `DocTag` (
  `DocId` int(11) NOT NULL,
  `TagId` int(11) NOT NULL,
  KEY `ItemId` (`DocId`) USING BTREE,
  KEY `TagId` (`TagId`),
  CONSTRAINT `DocId` FOREIGN KEY (`DocId`) REFERENCES `Documents` (`DocId`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `TagId` FOREIGN KEY (`TagId`) REFERENCES `Tags` (`TagId`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Document to Tag association';

-- Daten Export vom Benutzer nicht ausgewählt

-- Exportiere Struktur von Tabelle scanned_doc_db.Documents
CREATE TABLE IF NOT EXISTS `Documents` (
  `DocId` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(256) NOT NULL,
  `Path` text NOT NULL,
  `Date` date NOT NULL,
  `Summary` text NOT NULL,
  `OCR` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`DocId`) USING BTREE,
  UNIQUE KEY `Name` (`Name`),
  KEY `Date` (`Date`),
  FULLTEXT KEY `Summary` (`Summary`),
  FULLTEXT KEY `OCR` (`OCR`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Daten Export vom Benutzer nicht ausgewählt

-- Exportiere Struktur von Tabelle scanned_doc_db.Tags
CREATE TABLE IF NOT EXISTS `Tags` (
  `TagId` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(256) NOT NULL,
  PRIMARY KEY (`TagId`),
  UNIQUE KEY `Name` (`Name`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Keywords';

-- Daten Export vom Benutzer nicht ausgewählt

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
