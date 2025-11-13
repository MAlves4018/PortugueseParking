/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.4.7-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: 127.0.0.1    Database: django-database
-- ------------------------------------------------------
-- Server version	11.8.3-MariaDB-ubu2404

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES
(1,'Can add log entry',1,'add_logentry'),
(2,'Can change log entry',1,'change_logentry'),
(3,'Can delete log entry',1,'delete_logentry'),
(4,'Can view log entry',1,'view_logentry'),
(5,'Can add permission',2,'add_permission'),
(6,'Can change permission',2,'change_permission'),
(7,'Can delete permission',2,'delete_permission'),
(8,'Can view permission',2,'view_permission'),
(9,'Can add group',3,'add_group'),
(10,'Can change group',3,'change_group'),
(11,'Can delete group',3,'delete_group'),
(12,'Can view group',3,'view_group'),
(13,'Can add content type',4,'add_contenttype'),
(14,'Can change content type',4,'change_contenttype'),
(15,'Can delete content type',4,'delete_contenttype'),
(16,'Can view content type',4,'view_contenttype'),
(17,'Can add session',5,'add_session'),
(18,'Can change session',5,'change_session'),
(19,'Can delete session',5,'delete_session'),
(20,'Can view session',5,'view_session'),
(21,'Can add customer base',6,'add_customerbase'),
(22,'Can change customer base',6,'change_customerbase'),
(23,'Can delete customer base',6,'delete_customerbase'),
(24,'Can view customer base',6,'view_customerbase'),
(25,'Can add customer',7,'add_customer'),
(26,'Can change customer',7,'change_customer'),
(27,'Can delete customer',7,'delete_customer'),
(28,'Can view customer',7,'view_customer'),
(29,'Can add product base',8,'add_productbase'),
(30,'Can change product base',8,'change_productbase'),
(31,'Can delete product base',8,'delete_productbase'),
(32,'Can view product base',8,'view_productbase'),
(33,'Can add product',9,'add_product'),
(34,'Can change product',9,'change_product'),
(35,'Can delete product',9,'delete_product'),
(36,'Can view product',9,'view_product'),
(37,'Can add order',10,'add_order'),
(38,'Can change order',10,'change_order'),
(39,'Can delete order',10,'delete_order'),
(40,'Can view order',10,'view_order'),
(41,'Can add order position',11,'add_orderposition'),
(42,'Can change order position',11,'change_orderposition'),
(43,'Can delete order position',11,'delete_orderposition'),
(44,'Can view order position',11,'view_orderposition');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customer_base`
--

DROP TABLE IF EXISTS `customer_base`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer_base` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer_base`
--

LOCK TABLES `customer_base` WRITE;
/*!40000 ALTER TABLE `customer_base` DISABLE KEYS */;
INSERT INTO `customer_base` VALUES
(1,'pbkdf2_sha256$1000000$CJTaowElxulsHQaNgReHq2$ZfqK4XUs/YsfwWbvcOwY7AvRdiHPLYkicN1dWq9RGJs=','2025-09-06 12:37:16.000000',1,'admin','','','admin@localhost',1,1,'2025-09-06 12:37:06.000000');
/*!40000 ALTER TABLE `customer_base` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customer_base_groups`
--

DROP TABLE IF EXISTS `customer_base_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer_base_groups` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `customerbase_id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `customer_base_groups_customerbase_id_group_id_db228ff1_uniq` (`customerbase_id`,`group_id`),
  KEY `customer_base_groups_group_id_56661d98_fk_auth_group_id` (`group_id`),
  CONSTRAINT `customer_base_groups_customerbase_id_185d7ebf_fk_customer_` FOREIGN KEY (`customerbase_id`) REFERENCES `customer_base` (`id`),
  CONSTRAINT `customer_base_groups_group_id_56661d98_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer_base_groups`
--

LOCK TABLES `customer_base_groups` WRITE;
/*!40000 ALTER TABLE `customer_base_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `customer_base_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customer_base_user_permissions`
--

DROP TABLE IF EXISTS `customer_base_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer_base_user_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `customerbase_id` bigint(20) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `customer_base_user_permi_customerbase_id_permissi_56e18a6f_uniq` (`customerbase_id`,`permission_id`),
  KEY `customer_base_user_p_permission_id_e2ce72a2_fk_auth_perm` (`permission_id`),
  CONSTRAINT `customer_base_user_p_customerbase_id_5db8bcfd_fk_customer_` FOREIGN KEY (`customerbase_id`) REFERENCES `customer_base` (`id`),
  CONSTRAINT `customer_base_user_p_permission_id_e2ce72a2_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer_base_user_permissions`
--

LOCK TABLES `customer_base_user_permissions` WRITE;
/*!40000 ALTER TABLE `customer_base_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `customer_base_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customer_concrete`
--

DROP TABLE IF EXISTS `customer_concrete`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer_concrete` (
  `customerbase_ptr_id` bigint(20) NOT NULL,
  `credit` double DEFAULT NULL,
  PRIMARY KEY (`customerbase_ptr_id`),
  CONSTRAINT `customer_concrete_customerbase_ptr_id_f32f16d7_fk_customer_` FOREIGN KEY (`customerbase_ptr_id`) REFERENCES `customer_base` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer_concrete`
--

LOCK TABLES `customer_concrete` WRITE;
/*!40000 ALTER TABLE `customer_concrete` DISABLE KEYS */;
INSERT INTO `customer_concrete` VALUES
(1,100);
/*!40000 ALTER TABLE `customer_concrete` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_customer_` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_customer_` FOREIGN KEY (`user_id`) REFERENCES `customer_concrete` (`customerbase_ptr_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES
(1,'2025-09-06 12:37:31.660221','1','Product1',1,'[{\"added\": {}}]',9,1),
(2,'2025-09-06 12:38:42.119403','2','Product2',1,'[{\"added\": {}}]',9,1),
(3,'2025-09-06 12:38:58.910152','1','admin',2,'[{\"changed\": {\"fields\": [\"Credit\"]}}]',7,1);
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES
(1,'admin','logentry'),
(3,'auth','group'),
(2,'auth','permission'),
(4,'contenttypes','contenttype'),
(7,'customers','customer'),
(6,'customers','customerbase'),
(10,'orders','order'),
(11,'orders','orderposition'),
(9,'products','product'),
(8,'products','productbase'),
(5,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES
(1,'contenttypes','0001_initial','2025-09-06 12:37:04.602699'),
(2,'contenttypes','0002_remove_content_type_name','2025-09-06 12:37:04.673245'),
(3,'auth','0001_initial','2025-09-06 12:37:04.923467'),
(4,'auth','0002_alter_permission_name_max_length','2025-09-06 12:37:04.963862'),
(5,'auth','0003_alter_user_email_max_length','2025-09-06 12:37:04.967518'),
(6,'auth','0004_alter_user_username_opts','2025-09-06 12:37:04.970439'),
(7,'auth','0005_alter_user_last_login_null','2025-09-06 12:37:04.973530'),
(8,'auth','0006_require_contenttypes_0002','2025-09-06 12:37:04.974764'),
(9,'auth','0007_alter_validators_add_error_messages','2025-09-06 12:37:04.977825'),
(10,'auth','0008_alter_user_username_max_length','2025-09-06 12:37:04.980649'),
(11,'auth','0009_alter_user_last_name_max_length','2025-09-06 12:37:04.983648'),
(12,'auth','0010_alter_group_name_max_length','2025-09-06 12:37:05.009271'),
(13,'auth','0011_update_proxy_permissions','2025-09-06 12:37:05.012076'),
(14,'auth','0012_alter_user_first_name_max_length','2025-09-06 12:37:05.015390'),
(15,'customers','0001_initial','2025-09-06 12:37:05.358961'),
(16,'admin','0001_initial','2025-09-06 12:37:05.465118'),
(17,'admin','0002_logentry_remove_auto_add','2025-09-06 12:37:05.469155'),
(18,'admin','0003_logentry_add_action_flag_choices','2025-09-06 12:37:05.473188'),
(19,'customers','0002_customer_credit','2025-09-06 12:37:05.518833'),
(20,'customers','0003_alter_customer_credit','2025-09-06 12:37:05.553690'),
(21,'products','0001_initial','2025-09-06 12:37:05.617202'),
(22,'orders','0001_initial','2025-09-06 12:37:05.816235'),
(23,'orders','0002_alter_orderposition_order','2025-09-06 12:37:05.823533'),
(24,'orders','0003_order_total_price','2025-09-06 12:37:05.869934'),
(25,'products','0002_product_price','2025-09-06 12:37:05.913880'),
(26,'products','0003_product_ek','2025-09-06 12:37:05.958909'),
(27,'products','0004_remove_product_ek','2025-09-06 12:37:05.986736'),
(28,'sessions','0001_initial','2025-09-06 12:37:06.036755');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES
('ghlusg59kfak0b7giq9wsixdnp9wjtyk','.eJxVjDsOwyAQBe9CHSEwyy9lep8BLbAEJxGWjF1FuXtsyUXSzsx7bxZwW2vYOi1hyuzKJLv8sojpSe0Q-YHtPvM0t3WZIj8SftrOxznT63a2fwcVe93XlkrKgApQFocktFBIKokM4HWW2rsoShyUsT6S8AOCAdqBVtK4QpZ9vvXpN_8:1uusAO:TvZHWPfs9igMcIv3VYPYeqxRrKrUgxe5LXs0w_hPCjY','2025-09-20 12:37:16.779130');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders_order`
--

DROP TABLE IF EXISTS `orders_order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders_order` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL,
  `total_price` double NOT NULL,
  PRIMARY KEY (`id`),
  KEY `orders_order_user_id_e9b59eb1_fk_customer_base_id` (`user_id`),
  CONSTRAINT `orders_order_user_id_e9b59eb1_fk_customer_base_id` FOREIGN KEY (`user_id`) REFERENCES `customer_base` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders_order`
--

LOCK TABLES `orders_order` WRITE;
/*!40000 ALTER TABLE `orders_order` DISABLE KEYS */;
/*!40000 ALTER TABLE `orders_order` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders_orderposition`
--

DROP TABLE IF EXISTS `orders_orderposition`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders_orderposition` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `pos` int(10) unsigned NOT NULL CHECK (`pos` >= 0),
  `quantity` int(11) NOT NULL,
  `price` double NOT NULL,
  `order_id` bigint(20) NOT NULL,
  `product_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `orders_orderposition_order_id_pos_fe96b808_uniq` (`order_id`,`pos`),
  KEY `orders_orderposition_product_id_ff5b8e10_fk_products_base_id` (`product_id`),
  CONSTRAINT `orders_orderposition_order_id_f3bd1a11_fk_orders_order_id` FOREIGN KEY (`order_id`) REFERENCES `orders_order` (`id`),
  CONSTRAINT `orders_orderposition_product_id_ff5b8e10_fk_products_base_id` FOREIGN KEY (`product_id`) REFERENCES `products_base` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders_orderposition`
--

LOCK TABLES `orders_orderposition` WRITE;
/*!40000 ALTER TABLE `orders_orderposition` DISABLE KEYS */;
/*!40000 ALTER TABLE `orders_orderposition` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products_base`
--

DROP TABLE IF EXISTS `products_base`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `products_base` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `description` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products_base`
--

LOCK TABLES `products_base` WRITE;
/*!40000 ALTER TABLE `products_base` DISABLE KEYS */;
INSERT INTO `products_base` VALUES
(1,'Product1','Description Product1'),
(2,'Product2','Description Product2');
/*!40000 ALTER TABLE `products_base` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products_simple`
--

DROP TABLE IF EXISTS `products_simple`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `products_simple` (
  `productbase_ptr_id` bigint(20) NOT NULL,
  `price` double NOT NULL,
  PRIMARY KEY (`productbase_ptr_id`),
  CONSTRAINT `products_simple_productbase_ptr_id_2636bd0f_fk_products_base_id` FOREIGN KEY (`productbase_ptr_id`) REFERENCES `products_base` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products_simple`
--

LOCK TABLES `products_simple` WRITE;
/*!40000 ALTER TABLE `products_simple` DISABLE KEYS */;
INSERT INTO `products_simple` VALUES
(1,11),
(2,13);
/*!40000 ALTER TABLE `products_simple` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2025-09-06 14:39:59
