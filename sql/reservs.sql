/*!40101 SET NAMES utf8 */;
/*!40014 SET FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET SQL_NOTES=0 */;
DROP TABLE IF EXISTS reservs;
CREATE TABLE `reservs` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'primary key',
  `userId` varchar(255) DEFAULT NULL,
  `createTime` datetime DEFAULT NULL COMMENT 'create time',
  `reservTime` datetime DEFAULT NULL,
  `endTime` DATETIME DEFAULT NULL ,
  `tablesCount` int DEFAULT NULL,
  `status` varchar(127) NOT NULL,
  `commentary` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb3;