/*
Navicat MySQL Data Transfer

Source Server         : 236
Source Server Version : 50631
Source Host           : 219.141.189.236:3306
Source Database       : customer

Target Server Type    : MYSQL
Target Server Version : 50631
File Encoding         : 65001

Date: 2016-10-26 16:55:16
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `t_customer`
-- ----------------------------
DROP TABLE IF EXISTS `t_customer`;
CREATE TABLE `t_customer` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(30) DEFAULT NULL,
  `grade` tinyint(3) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of t_customer
-- ----------------------------
INSERT INTO `t_customer` VALUES ('1', 'Google', '0');
INSERT INTO `t_customer` VALUES ('2', 'Baidu', '0');
INSERT INTO `t_customer` VALUES ('3', 'Alibaba', '0');
INSERT INTO `t_customer` VALUES ('4', 'Tencent', '0');
INSERT INTO `t_customer` VALUES ('5', '23123', '0');
INSERT INTO `t_customer` VALUES ('6', '111', '0');
INSERT INTO `t_customer` VALUES ('7', '111', '0');
INSERT INTO `t_customer` VALUES ('8', '111', '0');
INSERT INTO `t_customer` VALUES ('9', '111', '0');
INSERT INTO `t_customer` VALUES ('10', '111', '0');
INSERT INTO `t_customer` VALUES ('11', '123', '0');
INSERT INTO `t_customer` VALUES ('12', '123', '0');
INSERT INTO `t_customer` VALUES ('13', '111', '0');
INSERT INTO `t_customer` VALUES ('14', '111', '0');
INSERT INTO `t_customer` VALUES ('15', '死阿光', '0');
INSERT INTO `t_customer` VALUES ('16', '死阿光', '0');
INSERT INTO `t_customer` VALUES ('19', 'vsite_sample_2', '0');
INSERT INTO `t_customer` VALUES ('20', 'vsite_sample', '0');
INSERT INTO `t_customer` VALUES ('21', 'test1', '0');
INSERT INTO `t_customer` VALUES ('22', 'test1', '0');
INSERT INTO `t_customer` VALUES ('23', 'test1', '0');
INSERT INTO `t_customer` VALUES ('24', 'test1', '0');
INSERT INTO `t_customer` VALUES ('25', 'test1', '0');
INSERT INTO `t_customer` VALUES ('26', 'test1', '0');
INSERT INTO `t_customer` VALUES ('31', 'test1', '0');
INSERT INTO `t_customer` VALUES ('32', 'test1', '0');
INSERT INTO `t_customer` VALUES ('33', 'test1', '0');
INSERT INTO `t_customer` VALUES ('34', 'test111', '0');
INSERT INTO `t_customer` VALUES ('35', 'test111', '0');
INSERT INTO `t_customer` VALUES ('36', 'test111', '0');
INSERT INTO `t_customer` VALUES ('37', 'test111', '0');
INSERT INTO `t_customer` VALUES ('38', 'test111', '0');
INSERT INTO `t_customer` VALUES ('40', 'test111111', '0');
INSERT INTO `t_customer` VALUES ('41', 'tesun', '0');

-- ----------------------------
-- Table structure for `t_customer_ip`
-- ----------------------------
DROP TABLE IF EXISTS `t_customer_ip`;
CREATE TABLE `t_customer_ip` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `customer_id` int(10) unsigned NOT NULL COMMENT '客户的id',
  `netip` int(11) unsigned DEFAULT NULL COMMENT '整数形式的ip',
  `netip_str` varchar(16) NOT NULL COMMENT '用户所拥有的子网ip或单个ip',
  `mask_bit` tinyint(3) unsigned NOT NULL,
  `mask_int` int(11) unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `customer_id1` (`customer_id`) USING BTREE,
  CONSTRAINT `t_customer_ip_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `t_customer` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of t_customer_ip
-- ----------------------------
INSERT INTO `t_customer_ip` VALUES ('1', '1', '167810048', '10.0.148.0', '22', '4294966272');
INSERT INTO `t_customer_ip` VALUES ('2', '2', '167835648', '10.0.248.0', '24', '4294967040');
INSERT INTO `t_customer_ip` VALUES ('3', '2', '167807488', '10.0.138.0', '24', '4294967040');
INSERT INTO `t_customer_ip` VALUES ('4', '3', '167830528', '10.0.228.0', '24', '4294967040');
INSERT INTO `t_customer_ip` VALUES ('5', '3', '167802368', '10.0.118.0', '24', '4294967040');
INSERT INTO `t_customer_ip` VALUES ('6', '4', '167827968', '10.0.218.0', '24', '4294967040');
INSERT INTO `t_customer_ip` VALUES ('10', '19', '3232289792', '192.168.212.0', '24', '4294967040');
INSERT INTO `t_customer_ip` VALUES ('11', '20', '167827968', '10.0.218.0', '24', '4294967040');
INSERT INTO `t_customer_ip` VALUES ('12', '20', '3232289792', '192.168.212.0', '24', '4294967040');
INSERT INTO `t_customer_ip` VALUES ('14', '19', '3232289792', '192.168.212.0', '24', '4294967040');
