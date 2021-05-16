/*!40101 SET NAMES utf8 */;
/*!40014 SET FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET SQL_NOTES=0 */;
DROP TABLE IF EXISTS users;
CREATE TABLE `users` (
  `telegramId` int NOT NULL,
  `username` varchar(255) DEFAULT NULL,
  `firstName` varchar(255) DEFAULT NULL,
  `lastName` varchar(255) DEFAULT NULL,
  `phone` varchar(255) DEFAULT NULL,
  `commandName` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`telegramId`),
  UNIQUE KEY `telegramId` (`telegramId`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `phone` (`phone`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;