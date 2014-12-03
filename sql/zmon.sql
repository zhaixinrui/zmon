-- MySQL dump 10.13  Distrib 5.1.65, for unknown-linux-gnu (x86_64)
--
-- Host: 127.0.0.1    Database: zmon
-- ------------------------------------------------------
-- Server version	5.1.65

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `zmon`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `zmon` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `zmon`;

--
-- Table structure for table `exec`
--

DROP TABLE IF EXISTS `exec`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `exec` (
  `EXEC_ID` int(11) NOT NULL AUTO_INCREMENT,
  `NAME` char(100) DEFAULT NULL,
  `COMMAND` text,
  `PARAMETER_ID_LIST` text,
  PRIMARY KEY (`EXEC_ID`)
) ENGINE=MyISAM AUTO_INCREMENT=111 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host`
--

DROP TABLE IF EXISTS `host`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host` (
  `HOST_ID` int(11) NOT NULL AUTO_INCREMENT,
  `NAME` char(100) DEFAULT NULL,
  `IP` varchar(100) NOT NULL,
  PRIMARY KEY (`HOST_ID`)
) ENGINE=MyISAM AUTO_INCREMENT=5221 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_monitor`
--

DROP TABLE IF EXISTS `host_monitor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_monitor` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `HOST_ID` int(16) DEFAULT NULL,
  `MONITOR_ID` int(16) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=132659 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `module`
--

DROP TABLE IF EXISTS `module`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `module` (
  `module_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '模块ID',
  `product` varchar(45) NOT NULL,
  `module_name` varchar(45) NOT NULL,
  `monitor_ids` varchar(253) NOT NULL,
  `module_type` varchar(5) NOT NULL,
  `module_value` varchar(253) NOT NULL,
  `current_status` int(11) NOT NULL,
  `ifc_datas` varchar(511) NOT NULL,
  PRIMARY KEY (`module_id`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COMMENT='产品线-模块信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `monitor`
--

DROP TABLE IF EXISTS `monitor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `monitor` (
  `MONITOR_ID` int(11) NOT NULL AUTO_INCREMENT,
  `NAME` char(100) DEFAULT NULL,
  `LOGPATH` char(100) DEFAULT NULL,
  `PRODUCT` char(100) DEFAULT NULL,
  `BNS` varchar(100) NOT NULL,
  `ZCM_ADDR` char(100) DEFAULT NULL,
  `REWORK_TIME` float DEFAULT '0.1',
  `REPORT_TIME` int(10) DEFAULT '10',
  `MAX_TIME` int(10) DEFAULT '1000000',
  `HIGH_WATER_MARK` int(10) DEFAULT '1024',
  `GREP` text,
  `KEY_ID_LIST` text,
  `VALUE_ID_LIST` text,
  `REGULAR_ID_LIST` text,
  `EXEC_ID_LIST` text,
  `UITREE` text,
  `UICHART` text,
  `GREPV` text NOT NULL,
  PRIMARY KEY (`MONITOR_ID`),
  KEY `NAME_2` (`NAME`)
) ENGINE=MyISAM AUTO_INCREMENT=879 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `node`
--

DROP TABLE IF EXISTS `node`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `node` (
  `NODE_ID` int(11) NOT NULL AUTO_INCREMENT,
  `NAME` char(100) DEFAULT NULL,
  `UNIT` char(100) DEFAULT NULL,
  `DIVIDE` tinyint(1) DEFAULT NULL,
  `DIVIDEND` char(100) DEFAULT NULL,
  `DIVISOR` char(100) DEFAULT NULL,
  `HIDDEN` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`NODE_ID`)
) ENGINE=MyISAM AUTO_INCREMENT=14 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `receiver`
--

DROP TABLE IF EXISTS `receiver`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `receiver` (
  `RECEIVER_ID` int(11) NOT NULL AUTO_INCREMENT,
  `PRODUCT_ID` int(11) NOT NULL,
  `ZCMKEY` tinytext NOT NULL,
  `MOBILE` text NOT NULL,
  `MAIL` text NOT NULL,
  PRIMARY KEY (`RECEIVER_ID`)
) ENGINE=MyISAM AUTO_INCREMENT=64 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `redis`
--

DROP TABLE IF EXISTS `redis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `redis` (
  `REDIS_ID` int(11) NOT NULL AUTO_INCREMENT,
  `TYPE` char(100) DEFAULT NULL,
  `IP` char(100) DEFAULT NULL,
  `PORT` int(10) DEFAULT '6379',
  PRIMARY KEY (`REDIS_ID`)
) ENGINE=MyISAM AUTO_INCREMENT=31 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `regular`
--

DROP TABLE IF EXISTS `regular`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `regular` (
  `REGULAR_ID` int(11) NOT NULL AUTO_INCREMENT,
  `NAME` char(100) DEFAULT NULL,
  `EXPRESSION` text,
  `TRANSFORM` char(10) DEFAULT NULL,
  PRIMARY KEY (`REGULAR_ID`)
) ENGINE=MyISAM AUTO_INCREMENT=10655 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `threshold`
--

DROP TABLE IF EXISTS `threshold`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `threshold` (
  `THRESHOLD_ID` int(11) NOT NULL AUTO_INCREMENT,
  `PRODUCT_ID` int(11) NOT NULL,
  `ZCMKEY` char(100) NOT NULL,
  `QPS_UPPER` int(11) DEFAULT NULL,
  `QPS_FLOOR` int(11) DEFAULT NULL,
  `CHANGE_RATE_UP` int(11) DEFAULT NULL,
  `CHANGE_RATE_DOWN` int(11) NOT NULL,
  `SHIELD_TIME` text NOT NULL,
  PRIMARY KEY (`THRESHOLD_ID`)
) ENGINE=MyISAM AUTO_INCREMENT=196 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `USER_ID` int(11) NOT NULL AUTO_INCREMENT,
  `USERNAME` char(100) DEFAULT NULL,
  `PRODUCT` text,
  PRIMARY KEY (`USER_ID`),
  UNIQUE KEY `USERNAME` (`USERNAME`)
) ENGINE=MyISAM AUTO_INCREMENT=642 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `whitelist`
--

DROP TABLE IF EXISTS `whitelist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `whitelist` (
  `WHITELIST_ID` int(11) NOT NULL AUTO_INCREMENT,
  `PRODUCT_ID` int(11) NOT NULL,
  `ZCMKEY` text,
  PRIMARY KEY (`WHITELIST_ID`)
) ENGINE=MyISAM AUTO_INCREMENT=43 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2014-12-01 15:56:03
