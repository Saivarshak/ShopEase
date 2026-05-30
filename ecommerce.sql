-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: shopeasy
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */
;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */
;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */
;
/*!50503 SET NAMES utf8mb4 */
;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */
;
/*!40103 SET TIME_ZONE='+00:00' */
;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */
;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */
;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */
;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */
;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!50503 SET character_set_client = utf8mb4 */
;
CREATE TABLE `auth_group` (
    `id` int NOT NULL AUTO_INCREMENT,
    `name` varchar(150) NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `name` (`name`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */
;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */
;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!50503 SET character_set_client = utf8mb4 */
;
CREATE TABLE `auth_group_permissions` (
    `id` int NOT NULL AUTO_INCREMENT,
    `group_id` int NOT NULL,
    `permission_id` int NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`, `permission_id`),
    KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
    CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
    CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */
;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */
;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!50503 SET character_set_client = utf8mb4 */
;
CREATE TABLE `auth_permission` (
    `id` int NOT NULL AUTO_INCREMENT,
    `name` varchar(255) NOT NULL,
    `content_type_id` int NOT NULL,
    `codename` varchar(100) NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`, `codename`),
    CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE = InnoDB AUTO_INCREMENT = 77 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */
;
INSERT INTO
    `auth_permission`
VALUES (
        1,
        'Can add log entry',
        11,
        'add_logentry'
    ),
    (
        2,
        'Can change log entry',
        11,
        'change_logentry'
    ),
    (
        3,
        'Can delete log entry',
        11,
        'delete_logentry'
    ),
    (
        4,
        'Can view log entry',
        11,
        'view_logentry'
    ),
    (
        5,
        'Can add permission',
        12,
        'add_permission'
    ),
    (
        6,
        'Can change permission',
        12,
        'change_permission'
    ),
    (
        7,
        'Can delete permission',
        12,
        'delete_permission'
    ),
    (
        8,
        'Can view permission',
        12,
        'view_permission'
    ),
    (
        9,
        'Can add group',
        13,
        'add_group'
    ),
    (
        10,
        'Can change group',
        13,
        'change_group'
    ),
    (
        11,
        'Can delete group',
        13,
        'delete_group'
    ),
    (
        12,
        'Can view group',
        13,
        'view_group'
    ),
    (
        13,
        'Can add user',
        14,
        'add_user'
    ),
    (
        14,
        'Can change user',
        14,
        'change_user'
    ),
    (
        15,
        'Can delete user',
        14,
        'delete_user'
    ),
    (
        16,
        'Can view user',
        14,
        'view_user'
    ),
    (
        17,
        'Can add content type',
        15,
        'add_contenttype'
    ),
    (
        18,
        'Can change content type',
        15,
        'change_contenttype'
    ),
    (
        19,
        'Can delete content type',
        15,
        'delete_contenttype'
    ),
    (
        20,
        'Can view content type',
        15,
        'view_contenttype'
    ),
    (
        21,
        'Can add session',
        16,
        'add_session'
    ),
    (
        22,
        'Can change session',
        16,
        'change_session'
    ),
    (
        23,
        'Can delete session',
        16,
        'delete_session'
    ),
    (
        24,
        'Can view session',
        16,
        'view_session'
    ),
    (
        25,
        'Can add category',
        17,
        'add_category'
    ),
    (
        26,
        'Can change category',
        17,
        'change_category'
    ),
    (
        27,
        'Can delete category',
        17,
        'delete_category'
    ),
    (
        28,
        'Can view category',
        17,
        'view_category'
    ),
    (
        29,
        'Can add sub category',
        20,
        'add_subcategory'
    ),
    (
        30,
        'Can change sub category',
        20,
        'change_subcategory'
    ),
    (
        31,
        'Can delete sub category',
        20,
        'delete_subcategory'
    ),
    (
        32,
        'Can view sub category',
        20,
        'view_subcategory'
    ),
    (
        33,
        'Can add men category',
        21,
        'add_mencategory'
    ),
    (
        34,
        'Can change men category',
        21,
        'change_mencategory'
    ),
    (
        35,
        'Can delete men category',
        21,
        'delete_mencategory'
    ),
    (
        36,
        'Can view men category',
        21,
        'view_mencategory'
    ),
    (
        37,
        'Can add women category',
        22,
        'add_womencategory'
    ),
    (
        38,
        'Can change women category',
        22,
        'change_womencategory'
    ),
    (
        39,
        'Can delete women category',
        22,
        'delete_womencategory'
    ),
    (
        40,
        'Can view women category',
        22,
        'view_womencategory'
    ),
    (
        41,
        'Can add kids category',
        23,
        'add_kidscategory'
    ),
    (
        42,
        'Can change kids category',
        23,
        'change_kidscategory'
    ),
    (
        43,
        'Can delete kids category',
        23,
        'delete_kidscategory'
    ),
    (
        44,
        'Can view kids category',
        23,
        'view_kidscategory'
    ),
    (
        45,
        'Can add site asset',
        24,
        'add_siteasset'
    ),
    (
        46,
        'Can change site asset',
        24,
        'change_siteasset'
    ),
    (
        47,
        'Can delete site asset',
        24,
        'delete_siteasset'
    ),
    (
        48,
        'Can view site asset',
        24,
        'view_siteasset'
    ),
    (
        49,
        'Can add page asset',
        25,
        'add_pageasset'
    ),
    (
        50,
        'Can change page asset',
        25,
        'change_pageasset'
    ),
    (
        51,
        'Can delete page asset',
        25,
        'delete_pageasset'
    ),
    (
        52,
        'Can view page asset',
        25,
        'view_pageasset'
    ),
    (
        53,
        'Can add home content',
        26,
        'add_homecontent'
    ),
    (
        54,
        'Can change home content',
        26,
        'change_homecontent'
    ),
    (
        55,
        'Can delete home content',
        26,
        'delete_homecontent'
    ),
    (
        56,
        'Can view home content',
        26,
        'view_homecontent'
    ),
    (
        57,
        'Can add product',
        18,
        'add_product'
    ),
    (
        58,
        'Can change product',
        18,
        'change_product'
    ),
    (
        59,
        'Can delete product',
        18,
        'delete_product'
    ),
    (
        60,
        'Can view product',
        18,
        'view_product'
    ),
    (
        61,
        'Can add product variant',
        19,
        'add_productvariant'
    ),
    (
        62,
        'Can change product variant',
        19,
        'change_productvariant'
    ),
    (
        63,
        'Can delete product variant',
        19,
        'delete_productvariant'
    ),
    (
        64,
        'Can view product variant',
        19,
        'view_productvariant'
    ),
    (
        65,
        'Can add cart item',
        27,
        'add_cartitem'
    ),
    (
        66,
        'Can change cart item',
        27,
        'change_cartitem'
    ),
    (
        67,
        'Can delete cart item',
        27,
        'delete_cartitem'
    ),
    (
        68,
        'Can view cart item',
        27,
        'view_cartitem'
    ),
    (
        69,
        'Can add order',
        28,
        'add_order'
    ),
    (
        70,
        'Can change order',
        28,
        'change_order'
    ),
    (
        71,
        'Can delete order',
        28,
        'delete_order'
    ),
    (
        72,
        'Can view order',
        28,
        'view_order'
    ),
    (
        73,
        'Can add order item',
        29,
        'add_orderitem'
    ),
    (
        74,
        'Can change order item',
        29,
        'change_orderitem'
    ),
    (
        75,
        'Can delete order item',
        29,
        'delete_orderitem'
    ),
    (
        76,
        'Can view order item',
        29,
        'view_orderitem'
    );
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */
;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!50503 SET character_set_client = utf8mb4 */
;
CREATE TABLE `auth_user` (
    `id` int NOT NULL AUTO_INCREMENT,
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
) ENGINE = InnoDB AUTO_INCREMENT = 6 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */
;
INSERT INTO
    `auth_user`
VALUES (
        3,
        'pbkdf2_sha256$1000000$A2BMoMdtQAwTbrzjFAHQ7W$cS6nzh5C6qnf39fubA3i6K8S07qp87SDAwGtNquxG7U=',
        '2026-04-01 13:36:15.299251',
        1,
        'saivarshak',
        '',
        '',
        'saivarshak14@gmail.com',
        1,
        1,
        '2026-03-14 12:41:32.506856'
    );
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */
;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!50503 SET character_set_client = utf8mb4 */
;
CREATE TABLE `auth_user_groups` (
    `id` int NOT NULL AUTO_INCREMENT,
    `user_id` int NOT NULL,
    `group_id` int NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`, `group_id`),
    KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
    CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
    CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */
;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */
;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!50503 SET character_set_client = utf8mb4 */
;
CREATE TABLE `auth_user_user_permissions` (
    `id` int NOT NULL AUTO_INCREMENT,
    `user_id` int NOT NULL,
    `permission_id` int NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`, `permission_id`),
    KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
    CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
    CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */
;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */
;
UNLOCK TABLES;

--
-- Table structure for table `cart_items`
--

DROP TABLE IF EXISTS `cart_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!50503 SET character_set_client = utf8mb4 */
;
CREATE TABLE `cart_items` (
    `cart_item_id` int NOT NULL AUTO_INCREMENT,
    `user_id` int NOT NULL,
    `product_id` int NOT NULL,
    `quantity` int unsigned NOT NULL,
    `created_at` datetime(6) NOT NULL,
    `updated_at` datetime(6) NOT NULL,
    `selected_size` varchar(50) DEFAULT NULL,
    PRIMARY KEY (`cart_item_id`),
    UNIQUE KEY `cart_items_user_id_product_id_selected_size_fce88720_uniq` (
        `user_id`,
        `product_id`,
        `selected_size`
    ),
    KEY `cart_items_product_id_9398bb89_fk_products_product_id` (`product_id`),
    KEY `cart_items_user_id_74745f54` (`user_id`),
    CONSTRAINT `cart_items_product_id_9398bb89_fk_products_product_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`),
    CONSTRAINT `cart_items_user_id_74745f54_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
    CONSTRAINT `cart_items_chk_1` CHECK ((`quantity` >= 0))
) ENGINE = InnoDB AUTO_INCREMENT = 19 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;

--
-- Dumping data for table `cart_items`
--

LOCK TABLES `cart_items` WRITE;
/*!40000 ALTER TABLE `cart_items` DISABLE KEYS */
;
INSERT INTO
    `cart_items`
VALUES (
        18,
        3,
        28,
        4,
        '2026-04-01 13:39:24.281990',
        '2026-04-01 13:39:24.282033',
        NULL
    );
/*!40000 ALTER TABLE `cart_items` ENABLE KEYS */
;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!50503 SET character_set_client = utf8mb4 */
;
CREATE TABLE `categories` (
    `category_id` int NOT NULL AUTO_INCREMENT,
    `category_name` varchar(100) NOT NULL,
    `image` varchar(255) DEFAULT NULL,
    PRIMARY KEY (`category_id`),
    UNIQUE KEY `category_name` (`category_name`)
) ENGINE = InnoDB AUTO_INCREMENT = 13 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */
;
INSERT INTO
    `categories`
VALUES (1, 'mens', 'images/men.jpg'),
    (
        2,
        'womens',
        'categories/women.jpeg'
    ),
    (
        3,
        'kids',
        'categories/kid.jpeg'
    );
/*!40000 ALTER TABLE `categories` ENABLE KEYS */
;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!50503 SET character_set_client = utf8mb4 */
;
CREATE TABLE `django_admin_log` (
    `id` int NOT NULL AUTO_INCREMENT,
    `action_time` datetime(6) NOT NULL,
    `object_id` longtext,
    `object_repr` varchar(200) NOT NULL,
    `action_flag` smallint unsigned NOT NULL,
    `change_message` longtext NOT NULL,
    `content_type_id` int DEFAULT NULL,
    `user_id` int NOT NULL,
    PRIMARY KEY (`id`),
    KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
    KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
    CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
    CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
    CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE = InnoDB AUTO_INCREMENT = 10 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */
;
INSERT INTO
    `django_admin_log`
VALUES (
        4,
        '2026-03-14 14:42:44.678208',
        '11',
        'shirt1',
        1,
        '[{\"added\": {}}]',
        17,
        3
    ),
    (
        5,
        '2026-03-14 14:42:55.636293',
        '11',
        'shirt1',
        3,
        '',
        17,
        3
    ),
    (
        6,
        '2026-03-30 18:23:37.038904',
        '12',
        'College Student',
        1,
        '[{\"added\": {}}]',
        17,
        3
    ),
    (
        7,
        '2026-03-30 18:25:02.910169',
        '4',
        'saivarshak15@gmail.com',
        3,
        '',
        14,
        3
    ),
    (
        8,
        '2026-03-30 18:25:02.910268',
        '5',
        'venumadhvi14@gmail.com',
        3,
        '',
        14,
        3
    ),
    (
        9,
        '2026-03-30 18:25:31.726326',
        '12',
        'College Student',
        3,
        '',
        17,
        3
    );
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */
;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!50503 SET character_set_client = utf8mb4 */
;
CREATE TABLE `django_content_type` (
    `id` int NOT NULL AUTO_INCREMENT,
    `app_label` varchar(100) NOT NULL,
    `model` varchar(100) NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`, `model`)
) ENGINE = InnoDB AUTO_INCREMENT = 30 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */
;
INSERT INTO
    `django_content_type`
VALUES (11, 'admin', 'logentry'),
    (13, 'auth', 'group'),
    (12, 'auth', 'permission'),
    (14, 'auth', 'user'),
    (
        15,
        'contenttypes',
        'contenttype'
    ),
    (16, 'sessions', 'session'),
    (27, 'store', 'cartitem'),
    (17, 'store', 'category'),
    (26, 'store', 'homecontent'),
    (23, 'store', 'kidscategory'),
    (21, 'store', 'mencategory'),
    (28, 'store', 'order'),
    (29, 'store', 'orderitem'),
    (25, 'store', 'pageasset'),
    (18, 'store', 'product'),
    (19, 'store', 'productvariant'),
    (24, 'store', 'siteasset'),
    (20, 'store', 'subcategory'),
    (22, 'store', 'womencategory');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */
;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!50503 SET character_set_client = utf8mb4 */
;
CREATE TABLE `django_migrations` (
    `id` bigint NOT NULL AUTO_INCREMENT,
    `app` varchar(255) NOT NULL,
    `name` varchar(255) NOT NULL,
    `applied` datetime(6) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE = InnoDB AUTO_INCREMENT = 45 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */
;
INSERT INTO
    `django_migrations`
VALUES (
        21,
        'contenttypes',
        '0001_initial',
        '2026-03-14 12:39:08.719403'
    ),
    (
        22,
        'auth',
        '0001_initial',
        '2026-03-14 12:39:08.728507'
    ),
    (
        23,
        'admin',
        '0001_initial',
        '2026-03-14 12:39:08.736001'
    ),
    (
        24,
        'admin',
        '0002_logentry_remove_auto_add',
        '2026-03-14 12:39:08.744654'
    ),
    (
        25,
        'admin',
        '0003_logentry_add_action_flag_choices',
        '2026-03-14 12:39:08.752976'
    ),
    (
        26,
        'contenttypes',
        '0002_remove_content_type_name',
        '2026-03-14 12:39:08.760852'
    ),
    (
        27,
        'auth',
        '0002_alter_permission_name_max_length',
        '2026-03-14 12:39:08.770695'
    ),
    (
        28,
        'auth',
        '0003_alter_user_email_max_length',
        '2026-03-14 12:39:08.780209'
    ),
    (
        29,
        'auth',
        '0004_alter_user_username_opts',
        '2026-03-14 12:39:08.787471'
    ),
    (
        30,
        'auth',
        '0005_alter_user_last_login_null',
        '2026-03-14 12:39:08.795991'
    ),
    (
        31,
        'auth',
        '0006_require_contenttypes_0002',
        '2026-03-14 12:39:08.806751'
    ),
    (
        32,
        'auth',
        '0007_alter_validators_add_error_messages',
        '2026-03-14 12:39:08.816609'
    ),
    (
        33,
        'auth',
        '0008_alter_user_username_max_length',
        '2026-03-14 12:39:08.825634'
    ),
    (
        34,
        'auth',
        '0009_alter_user_last_name_max_length',
        '2026-03-14 12:39:08.835271'
    ),
    (
        35,
        'auth',
        '0010_alter_group_name_max_length',
        '2026-03-14 12:39:08.843366'
    ),
    (
        36,
        'auth',
        '0011_update_proxy_permissions',
        '2026-03-14 12:39:08.851373'
    ),
    (
        37,
        'auth',
        '0012_alter_user_first_name_max_length',
        '2026-03-14 12:39:08.858731'
    ),
    (
        38,
        'sessions',
        '0001_initial',
        '2026-03-14 12:39:08.867415'
    ),
    (
        39,
        'store',
        '0001_initial',
        '2026-03-14 12:39:08.882329'
    ),
    (
        40,
        'store',
        '0002_category_image_alter_product_discount_percent_and_more',
        '2026-03-14 12:47:14.228266'
    ),
    (
        41,
        'store',
        '0004_cartitem_persistent',
        '2026-03-30 09:05:07.170670'
    ),
    (
        42,
        'store',
        '0005_reconcile_state',
        '2026-03-30 14:35:21.000000'
    ),
    (
        43,
        'store',
        '0006_order_orderitem',
        '2026-03-30 10:03:31.930074'
    ),
    (
        44,
        'store',
        '0007_alter_cartitem_unique_together_and_more',
        '2026-03-30 18:16:02.943348'
    );
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */
;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!50503 SET character_set_client = utf8mb4 */
;
CREATE TABLE `django_session` (
    `session_key` varchar(40) NOT NULL,
    `session_data` longtext NOT NULL,
    `expire_date` datetime(6) NOT NULL,
    PRIMARY KEY (`session_key`),
    KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */
;
INSERT INTO
    `django_session`
VALUES (
        '51n51em2lfc79ts1d8cwqruhva6dxgk4',
        '.eJxVjDsOgzAQRO-yNbLM-ovL9JwBre0lkEQg8akQd4-RKJJqNPNm5oCO9m3o9pWXbswQwED1m0VKb54ukF80PWeR5mlbxiiuirjpKto58-dxd_8OBlqHsiab0cfYeExakZSefG-yZvQcVUyy96gsk2E2NcnGJa61tTI7pVBnlOU00bJBOAAthLoCdBBcEV_ceX4B5Yo-tw:1w78Vi:RSHWcjEzO2bo-NwExuXzhsJ4BLLHTFjWGQjTXCrnUck',
        '2026-04-13 09:02:14.850013'
    ),
    (
        '6nczet1go87r9z84be08arxtb7nnd354',
        '.eJxVjDsOg0AMRO_iGq0W7weHMn3OgLxrE0gikPhUiLsHJIqkGmnmzdug4XXpmnXWqekFaghQ_HaJ81uHc5AXD8_R5HFYpj6ZEzHXOpvHKPq5X-yfoOO5O94cBSmlG2H2jq0lpjaIVyRNLmXbErqoHFRDyfZWZS19jFYq59AL2kOaeVqg3gAj1GUBSEfs-xc2uD1t:1w77kr:zaQzjVkTA3DtO18L_bU7QXmAoioDFZTEAvUkUcHk8OU',
        '2026-04-13 08:13:49.000809'
    ),
    (
        'b6symlypu675lcgkl31g0kq2yfa1gwks',
        '.eJxVjLEOgzAQQ__lZhRxSSAhY_d-Azoul0JbgURgQvx7oWJoJ8t-tjdoaV36ds0yt0OEAAaK36wjfsl4gvik8TEpnsZlHjp1VtRFs7pPUd63q_t30FPuz7W1FiuN6KjR1hM51yUuozCx49qbpBuOWHrrxYtBU8aaJVkhXXFK_jhlmhcIG-gagi5AOwh4iP86g4fs-wejCkCS:1w7Gb4:wEWW_-VML2x6Z7L77ahTbmz64TeUIrqv4kRSrU7xXRI',
        '2026-04-13 17:40:18.639577'
    ),
    (
        'jlao42547u541e5m29srsotw6xmq3sl6',
        '.eJxVjMsOgyAQRf-FdUOQl-iy-34DGZix2DaYAK6M_15NXLTbe849G_OwtuTXSsXPyEZm2O13CxDflE-AL8jPhccltzIHfir8opU_FqTP_XL_AglqOt5gUboQBiejViCEAzcZ1CQdBRWimJxUlsAQmQ7E0EfqtLUCe6WkRimOaITS2Ljt-xcueTsR:1w79Vs:AUnoKtMNi6MGFoX8_pDGQp8LpHl5ppj2aQeKej5PSTg',
        '2026-04-13 10:06:28.104063'
    ),
    (
        'kgkfd28vjlemhaupmjnibq3jr2xq00e0',
        '.eJxVjDsOwyAQBe9CHSE-a4NTpvcZ0LIswUmEJWNXUe4eIblI2jcz7y0CHnsJR-MtLElchRWX3y0iPbl2kB5Y76ukte7bEmVX5EmbnNfEr9vp_h0UbKXXAKAHo7XDyYBHdC5mUokJydHobTYTJa08ePZstVVpJM7AaAbK2YvPF-EfOGQ:1w1OJr:YqyrFhP4vt09dWkiOIolO0I_CY9sXmS3JGglX7OonWQ',
        '2026-03-28 12:42:15.352074'
    ),
    (
        'm2nbg05tmylu2s4stmsui7zdmqmurcwn',
        '.eJxVjDsOgzAQBe_iOrLwB2wo03MGa727DiQRSNhUiLsnliiS9s28OUSAvUxhz7yFmcQgjLj9bhHwxUsF9ITlsUpcl7LNUVZFXjTLcSV-3y_3LzBBnurbWqtarZSDXlsP4FxM2BAjoMPOm6R7JNV469mzUaahDjlZBt1iSv4bRdiKGI7z_AAj4Duw:1w7HSo:bIy9nVj24_r6tSi-O7z6X2s-K9TbpDrKDt2w4P0XiB8',
        '2026-04-13 18:35:50.445710'
    ),
    (
        'msrbtcyo4mzn7z77e56gkpcqjmtrm3ia',
        '.eJxVjDsOgzAQBe_iOrLwB2wo03MGa727DiQRSNhUiLsnliiS9s28OUSAvUxhz7yFmcQgjLj9bhHwxUsF9ITlsUpcl7LNUVZFXjTLcSV-3y_3LzBBnurbWqtarZSDXlsP4FxM2BAjoMPOm6R7JNV469mzUaahDjlZBt1iSv4bRdiKGI7z_AAj4Duw:1w7vn2:-iRUvupmcOsoxm0HmDh178fHD6irb5T5LSdpzxEBV5w',
        '2026-04-15 13:39:24.292800'
    ),
    (
        'sufbsk779yge3asvgkhch6w9pqb0zh1v',
        '.eJxVjDkOgzAQRe8yNbLMeGHiMn3OgMb2EEgikFgqxN0DiCKpnv66Qs3L3NbLJGPdZQjgoPj1Iqe39EeQX9w_B5WGfh67qI6KutJJPYYsn_vV_TtoeWr3NfuMFOONMFnDWhNT47IVJIkmJt0QGi_sRFzJ-lYlKa33OlfGoM2o99PE4wxhBfQQygKwgoA76FTGnLAHtu0LXSJBNQ:1w783O:SyAxS17k-sMR3ODICFLkl13eoVq313Qrb5wR2KvMeYk',
        '2026-04-13 08:32:58.725739'
    );
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */
;
UNLOCK TABLES;

--
-- Table structure for table `home_content`
--

DROP TABLE IF EXISTS `home_content`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!50503 SET character_set_client = utf8mb4 */
;
CREATE TABLE `home_content` (
    `home_content_id` int NOT NULL AUTO_INCREMENT,
    `hero_subtitle` varchar(255) DEFAULT NULL,
    `hero_title` varchar(255) DEFAULT NULL,
    `hero_highlight` varchar(255) DEFAULT NULL,
    `hero_tagline` varchar(255) DEFAULT NULL,
    `hero_button_text` varchar(100) DEFAULT NULL,
    `hero_button_url` varchar(255) DEFAULT NULL,
    `is_active` tinyint(1) DEFAULT '1',
    `search_placeholder` varchar(255) DEFAULT NULL,
    `search_button_text` varchar(100) DEFAULT NULL,
    `nav_home_text` varchar(100) DEFAULT NULL,
    `nav_home_url` varchar(255) DEFAULT NULL,
    `nav_products_text` varchar(100) DEFAULT NULL,
    `nav_products_url` varchar(255) DEFAULT NULL,
    `nav_contact_text` varchar(100) DEFAULT NULL,
    `nav_contact_url` varchar(255) DEFAULT NULL,
    `nav_login_text` varchar(100) DEFAULT NULL,
    `nav_login_url` varchar(255) DEFAULT NULL,
    `category_section_title` varchar(255) DEFAULT NULL,
    `men_description` varchar(255) DEFAULT NULL,
    `women_description` varchar(255) DEFAULT NULL,
    `kids_description` varchar(255) DEFAULT NULL,
    `featured_section_title` varchar(255) DEFAULT NULL,
    `footer_text` varchar(255) DEFAULT NULL,
    `footer_brand_text` varchar(100) DEFAULT NULL,
    `footer_builder_text` varchar(100) DEFAULT NULL,
    PRIMARY KEY (`home_content_id`)
) ENGINE = InnoDB AUTO_INCREMENT = 2 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;

--
-- Dumping data for table `home_content`
--

LOCK TABLES `home_content` WRITE;
/*!40000 ALTER TABLE `home_content` DISABLE KEYS */
;
INSERT INTO
    `home_content`
VALUES (
        1,
        'For Modern Shoppers',
        'Relax,',
        'ShopEase',
        'Faster, Fairer, and Closer to You',
        'Explore Products',
        '/category_men/',
        1,
        'Search for products...',
        'Search',
        'Home',
        '/',
        'Products',
        '#featured-products',
        'Contact Us',
        '#',
        'Login',
        '/login/',
        'Shop by Category',
        'Casual wear, formals, accessories and more.',
        'Ethnic, western, and everything chic!',
        'Trendy and comfy styles for kids of all ages.',
        'Featured Products',
        'All rights reserved.',
        'ShopEase',
        'Varshak Shopeasy'
    );
/*!40000 ALTER TABLE `home_content` ENABLE KEYS */
;
UNLOCK TABLES;

--
-- Table structure for table `kids_categories`
--

DROP TABLE IF EXISTS `kids_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!50503 SET character_set_client = utf8mb4 */
;
CREATE TABLE `kids_categories` (
    `kids_category_id` int NOT NULL AUTO_INCREMENT,
    `category_id` int NOT NULL,
    `category_name` varchar(100) NOT NULL,
    `image` varchar(255) DEFAULT NULL,
    `description` text,
    `page_url` varchar(255) DEFAULT NULL,
    `is_active` tinyint(1) DEFAULT '1',
    `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`kids_category_id`),
    KEY `fk_kids_categories_category` (`category_id`),
    CONSTRAINT `fk_kids_categories_category` FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`) ON DELETE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 9 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;

--
-- Dumping data for table `kids_categories`
--

LOCK TABLES `kids_categories` WRITE;
/*!40000 ALTER TABLE `kids_categories` DISABLE KEYS */
;
INSERT INTO
    `kids_categories`
VALUES (
        1,
        3,
        'T-Shirts',
        'images/kids-tshirts.png',
        'Fun prints, breathable fabric, all-day wear.',
        '/kids_tshirts',
        1,
        '2026-03-29 16:18:14'
    ),
    (
        2,
        3,
        'Kids Dresses',
        'images/kids-dresses.png',
        'Cute and comfy dresses for all occasions.',
        '/kids_dresses',
        1,
        '2026-03-29 16:18:14'
    ),
    (
        3,
        3,
        'Toys',
        'images/kids-toys.png',
        'Smart, soft, and safe for learning & fun.',
        '/kids_toys',
        1,
        '2026-03-29 16:18:14'
    ),
    (
        4,
        3,
        'Footwear',
        'images/kids-footwear.png',
        'Stylish & trendy picks.',
        '/kids_footwear',
        1,
        '2026-03-29 16:18:14'
    );
/*!40000 ALTER TABLE `kids_categories` ENABLE KEYS */
;
UNLOCK TABLES;

--
-- Table structure for table `login`
--

DROP TABLE IF EXISTS `login`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!50503 SET character_set_client = utf8mb4 */
;
CREATE TABLE `login` (
    `id` int DEFAULT NULL,
    `name` varchar(200) DEFAULT NULL,
    `password` varchar(200) DEFAULT NULL,
    `email` varchar(200) DEFAULT NULL
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;

--
-- Dumping data for table `login`
--

LOCK TABLES `login` WRITE;
/*!40000 ALTER TABLE `login` DISABLE KEYS */
;
/*!40000 ALTER TABLE `login` ENABLE KEYS */
;
UNLOCK TABLES;

--
-- Table structure for table `men_categories`
--

DROP TABLE IF EXISTS `men_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!50503 SET character_set_client = utf8mb4 */
;
CREATE TABLE `men_categories` (
    `men_category_id` int NOT NULL AUTO_INCREMENT,
    `category_id` int NOT NULL,
    `category_name` varchar(100) NOT NULL,
    `image` varchar(255) DEFAULT NULL,
    `description` text,
    `page_url` varchar(255) DEFAULT NULL,
    `is_active` tinyint(1) DEFAULT '1',
    `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`men_category_id`),
    KEY `fk_men_categories_category` (`category_id`),
    CONSTRAINT `fk_men_categories_category` FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`) ON DELETE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 5 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;

--
-- Dumping data for table `men_categories`
--

LOCK TABLES `men_categories` WRITE;
/*!40000 ALTER TABLE `men_categories` DISABLE KEYS */
;
INSERT INTO
    `men_categories`
VALUES (
        1,
        1,
        'T-Shirts',
        'images/mens_tshirts.png',
        'Trendy and comfy styles.',
        '/mens_tshirts',
        1,
        '2026-03-29 15:51:50'
    ),
    (
        2,
        1,
        'Shirts',
        'images/mens_shirts.png',
        'Casual and formal shirts in all styles.',
        '/mens_shirts',
        1,
        '2026-03-29 15:51:50'
    ),
    (
        3,
        1,
        'Jeans',
        'images/mens_jeans.png',
        'Rugged, stylish denim for every day.',
        '/mens_jeans',
        1,
        '2026-03-29 15:51:50'
    ),
    (
        4,
        1,
        'Accessories',
        'images/mens_accessories.png',
        'Belts, watches & more.',
        '/accessories_men',
        1,
        '2026-03-29 15:51:50'
    );
/*!40000 ALTER TABLE `men_categories` ENABLE KEYS */
;
UNLOCK TABLES;

--
-- Table structure for table `order_items`
--

DROP TABLE IF EXISTS `order_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!50503 SET character_set_client = utf8mb4 */
;
CREATE TABLE `order_items` (
    `order_item_id` int NOT NULL AUTO_INCREMENT,
    `quantity` int unsigned NOT NULL,
    `unit_price` decimal(10, 2) NOT NULL,
    `line_total` decimal(10, 2) NOT NULL,
    `created_at` datetime(6) NOT NULL,
    `order_id` int NOT NULL,
    `product_id` int NOT NULL,
    `selected_size` varchar(50) DEFAULT NULL,
    PRIMARY KEY (`order_item_id`),
    KEY `order_items_order_id_412ad78b_fk_orders_order_id` (`order_id`),
    KEY `order_items_product_id_dd557d5a_fk_products_product_id` (`product_id`),
    CONSTRAINT `order_items_order_id_412ad78b_fk_orders_order_id` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`),
    CONSTRAINT `order_items_product_id_dd557d5a_fk_products_product_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`),
    CONSTRAINT `order_items_chk_1` CHECK ((`quantity` >= 0))
) ENGINE = InnoDB AUTO_INCREMENT = 5 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;

--
-- Dumping data for table `order_items`
--

LOCK TABLES `order_items` WRITE;
/*!40000 ALTER TABLE `order_items` DISABLE KEYS */
;
/*!40000 ALTER TABLE `order_items` ENABLE KEYS */
;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!50503 SET character_set_client = utf8mb4 */
;
CREATE TABLE `orders` (
    `order_id` int NOT NULL AUTO_INCREMENT,
    `full_name` varchar(255) NOT NULL,
    `phone_number` varchar(20) NOT NULL,
    `email` varchar(254) NOT NULL,
    `address` varchar(255) NOT NULL,
    `city` varchar(100) NOT NULL,
    `state` varchar(100) NOT NULL,
    `pincode` varchar(20) NOT NULL,
    `country` varchar(100) NOT NULL,
    `payment_method` varchar(50) NOT NULL,
    `subtotal` decimal(10, 2) NOT NULL,
    `total_items` int unsigned NOT NULL,
    `status` varchar(50) NOT NULL,
    `created_at` datetime(6) NOT NULL,
    `user_id` int NOT NULL,
    PRIMARY KEY (`order_id`),
    KEY `orders_user_id_7e2523fb_fk_auth_user_id` (`user_id`),
    CONSTRAINT `orders_user_id_7e2523fb_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
    CONSTRAINT `orders_chk_1` CHECK ((`total_items` >= 0))
) ENGINE = InnoDB AUTO_INCREMENT = 3 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */
;
/*!40000 ALTER TABLE `orders` ENABLE KEYS */
;
UNLOCK TABLES;

--
-- Table structure for table `page_assets`
--

DROP TABLE IF EXISTS `page_assets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!50503 SET character_set_client = utf8mb4 */
;
CREATE TABLE `page_assets` (
    `page_asset_id` int NOT NULL AUTO_INCREMENT,
    `page_key` varchar(100) NOT NULL,
    `asset_key` varchar(100) NOT NULL,
    `image_path` varchar(255) NOT NULL,
    `is_active` tinyint(1) DEFAULT '1',
    PRIMARY KEY (`page_asset_id`)
) ENGINE = InnoDB AUTO_INCREMENT = 15 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;

--
-- Dumping data for table `page_assets`
--

LOCK TABLES `page_assets` WRITE;
/*!40000 ALTER TABLE `page_assets` DISABLE KEYS */
;
INSERT INTO
    `page_assets`
VALUES (
        1,
        'category_men',
        'background',
        'images/bg.jpg',
        1
    ),
    (
        2,
        'category_women',
        'background',
        'images/bg.jpg',
        1
    ),
    (
        3,
        'category_kids',
        'background',
        'images/bg.jpg',
        1
    ),
    (
        4,
        'mens_shirts',
        'background',
        'images/shirt.jpg',
        1
    ),
    (
        5,
        'mens_tshirts',
        'background',
        'images/menstshirts.jpg',
        1
    ),
    (
        6,
        'mens_shirt_detail',
        'fallback_front',
        'images/mens_shirts.png',
        1
    ),
    (
        7,
        'mens_shirt_detail',
        'fallback_back',
        'images/mens_shirts.png',
        1
    ),
    (
        8,
        'mens_shirt_detail',
        'fallback_side',
        'images/mens_shirts.png',
        1
    ),
    (
        9,
        'mens_shirt_detail',
        'fallback_close',
        'images/mens_shirts.png',
        1
    ),
    (
        10,
        'mens_tshirt_detail',
        'fallback_front',
        'images/T-shirt.jpg',
        1
    ),
    (
        11,
        'mens_tshirt_detail',
        'fallback_side',
        'images/T-shirt side.jpg',
        1
    ),
    (
        12,
        'mens_tshirt_detail',
        'fallback_back',
        'images/T-shirt back.jpg',
        1
    ),
    (
        13,
        'mens_tshirt_detail',
        'fallback_close',
        'images/T-shirt close.jpg',
        1
    ),
    (
        14,
        'womens_footwear',
        'background',
        'images/women_footwear_bg.jpg',
        1
    );
/*!40000 ALTER TABLE `page_assets` ENABLE KEYS */
;
UNLOCK TABLES;

--
-- Table structure for table `product_variants`
--

DROP TABLE IF EXISTS `product_variants`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!50503 SET character_set_client = utf8mb4 */
;
CREATE TABLE `product_variants` (
    `variant_id` int NOT NULL AUTO_INCREMENT,
    `product_id` int NOT NULL,
    `size` varchar(10) DEFAULT NULL,
    `color` varchar(50) DEFAULT NULL,
    `quantity` int DEFAULT '0',
    `image1` varchar(255) DEFAULT NULL,
    `image2` varchar(255) DEFAULT NULL,
    `image3` varchar(255) DEFAULT NULL,
    `image4` varchar(255) DEFAULT NULL,
    PRIMARY KEY (`variant_id`),
    KEY `product_id` (`product_id`),
    CONSTRAINT `product_variants_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`)
) ENGINE = InnoDB AUTO_INCREMENT = 28 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;

--
-- Dumping data for table `product_variants`
--

LOCK TABLES `product_variants` WRITE;
/*!40000 ALTER TABLE `product_variants` DISABLE KEYS */
;
INSERT INTO
    `product_variants`
VALUES (
        1,
        27,
        'M',
        'Black',
        10,
        'men_shirt_black_front.jpg',
        'men_shirt_black_back.jpg',
        'men_shirt_black_side.jpg',
        'men_shirt_black_closeup.jpg'
    ),
    (
        2,
        35,
        'M',
        'Blue',
        10,
        'kids_tshirt_front.jpg',
        'kids_tshirt_back.jpg',
        'kids_tshirt_side.jpg',
        'kids_tshirt_close.jpg'
    ),
    (
        3,
        43,
        '30',
        'Black',
        8,
        'kids_shoe_front.jpg',
        'kids_shoe_back.jpg',
        'kids_shoe_side.jpg',
        'kids_shoe_close.jpg'
    ),
    (
        4,
        28,
        '32',
        'Blue',
        10,
        'mens_jeans_front.jpg',
        'mens_jeans_back.jpg',
        'mens_jeans_side.jpg',
        'mens_jeans_close.jpg'
    ),
    (
        5,
        31,
        '6',
        'Black',
        10,
        'women_footwear_front.jpg',
        'women_footwear_back.jpg',
        'women_footwear_side.jpg',
        'women_footwear_close.jpg'
    ),
    (
        7,
        30,
        'Free size',
        'White & Black',
        9,
        'women-western-dress_image1.jpg',
        'women-western-dress_image2.jpg',
        'women-western-dress_image3.jpg',
        'women-western-dress_image4.jpg'
    ),
    (
        21,
        32,
        'S',
        'White',
        3,
        'kids_shirt_front.jpg',
        'kids_shirt_side.jpg',
        'kids_shirt_back.jpg',
        'kids_shirt_close.jpg'
    ),
    (
        22,
        32,
        'M',
        'White',
        2,
        'kids_shirt_front.jpg',
        'kids_shirt_side.jpg',
        'kids_shirt_back.jpg',
        'kids_shirt_close.jpg'
    ),
    (
        23,
        32,
        'L',
        'White',
        2,
        'kids_shirt_front.jpg',
        'kids_shirt_side.jpg',
        'kids_shirt_back.jpg',
        'kids_shirt_close.jpg'
    ),
    (
        24,
        32,
        'Xl',
        'White',
        2,
        'kids_shirt_front.jpg',
        'kids_shirt_side.jpg',
        'kids_shirt_back.jpg',
        'kids_shirt_close.jpg'
    ),
    (
        25,
        29,
        'S',
        NULL,
        0,
        'women-ethnic-kurta_image1.jpg',
        'women-ethnic-kurta_image2.jpg',
        'women-ethnic-kurta_image3.jpg',
        'women-ethnic-kurta_image4.jpg'
    ),
    (
        27,
        45,
        'S',
        NULL,
        8,
        'kids-t-shirt_image1.jpg',
        'kids-t-shirt_image2.jpg',
        'kids-t-shirt_image3.jpg',
        'kids-t-shirt_image4.jpg'
    );
/*!40000 ALTER TABLE `product_variants` ENABLE KEYS */
;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!50503 SET character_set_client = utf8mb4 */
;
CREATE TABLE `products` (
    `product_id` int NOT NULL AUTO_INCREMENT,
    `product_name` varchar(255) NOT NULL,
    `brand` varchar(100) DEFAULT NULL,
    `category_id` int NOT NULL,
    `subcategory_id` int NOT NULL,
    `sku` varchar(100) NOT NULL,
    `price` decimal(10, 2) NOT NULL,
    `discount_percent` decimal(5, 2) DEFAULT '0.00',
    `offer_price` decimal(10, 2) GENERATED ALWAYS AS (
        (
            `price` - (
                (`price` * `discount_percent`) / 100
            )
        )
    ) STORED,
    `description` text,
    `is_active` tinyint(1) DEFAULT '1',
    PRIMARY KEY (`product_id`),
    UNIQUE KEY `sku` (`sku`),
    KEY `category_id` (`category_id`),
    KEY `subcategory_id` (`subcategory_id`),
    CONSTRAINT `products_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`),
    CONSTRAINT `products_ibfk_2` FOREIGN KEY (`subcategory_id`) REFERENCES `subcategories` (`subcategory_id`)
) ENGINE = InnoDB AUTO_INCREMENT = 46 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */
;
INSERT INTO
    `products` (
        `product_id`,
        `product_name`,
        `brand`,
        `category_id`,
        `subcategory_id`,
        `sku`,
        `price`,
        `discount_percent`,
        `description`,
        `is_active`
    )
VALUES (
        26,
        'Men Blue T-Shirt',
        'Levis',
        1,
        1,
        'MEN-TSHIRT-001',
        599.00,
        10.00,
        'Cotton casual t-shirt',
        1
    ),
    (
        27,
        'Men Black Shirt',
        'Allen Solly',
        1,
        2,
        'MEN-SHIRT-001',
        999.00,
        15.00,
        'Formal slim fit shirt',
        1
    ),
    (
        28,
        'Men Denim Jeans',
        'Wrangler',
        1,
        3,
        'MEN-JEANS-001',
        1499.00,
        20.00,
        'Slim fit denim jeans',
        1
    ),
    (
        29,
        'Women Ethnic Kurta',
        'Biba',
        2,
        4,
        'WOM-KURTA-001',
        799.00,
        10.00,
        'Traditional cotton kurta',
        1
    ),
    (
        30,
        'Women Western Dress',
        'Zara',
        2,
        5,
        'WOM-DRESS-001',
        1299.00,
        12.00,
        'Stylish western dress',
        1
    ),
    (
        31,
        'Women Sandals',
        'Bata',
        2,
        6,
        'WOM-FOOT-001',
        699.00,
        5.00,
        'Comfortable sandals',
        1
    ),
    (
        32,
        'Kids White T-Shirt',
        'H&M',
        3,
        7,
        'KID-TSHIRT-001',
        1000.00,
        10.00,
        'Soft cotton kids t-shirt',
        1
    ),
    (
        33,
        'Kids Party Dress',
        'Max',
        3,
        8,
        'KID-DRESS-001',
        899.00,
        10.00,
        'Kids party dress',
        1
    ),
    (
        34,
        'Kids Toy Set',
        'Funskool',
        3,
        9,
        'KID-TOY-001',
        499.00,
        0.00,
        'Educational toy set',
        1
    ),
    (
        35,
        'Kids Blue T-Shirt',
        'MiniStyle',
        3,
        7,
        'KIDS-TSHIRT-001',
        799.00,
        10.00,
        'Soft cotton kids t-shirt for daily wear.',
        1
    ),
    (
        43,
        'Kids Sport Shoes',
        'TinySteps',
        3,
        11,
        'KIDS-FOOT-001',
        1299.00,
        15.00,
        'Comfortable kids footwear for play and outdoor use.',
        1
    ),
    (
        45,
        'Kids T-Shirt',
        'Zara',
        3,
        7,
        'KID-TSHIRT-003',
        1000.00,
        20.00,
        'Kids Fashion',
        1
    );
/*!40000 ALTER TABLE `products` ENABLE KEYS */
;
UNLOCK TABLES;

--
-- Table structure for table `site_assets`
--

DROP TABLE IF EXISTS `site_assets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!50503 SET character_set_client = utf8mb4 */
;
CREATE TABLE `site_assets` (
    `asset_id` int NOT NULL AUTO_INCREMENT,
    `asset_key` varchar(100) NOT NULL,
    `image_path` varchar(255) NOT NULL,
    `is_active` tinyint(1) DEFAULT '1',
    PRIMARY KEY (`asset_id`),
    UNIQUE KEY `asset_key` (`asset_key`)
) ENGINE = InnoDB AUTO_INCREMENT = 4 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;

--
-- Dumping data for table `site_assets`
--

LOCK TABLES `site_assets` WRITE;
/*!40000 ALTER TABLE `site_assets` DISABLE KEYS */
;
INSERT INTO
    `site_assets`
VALUES (
        1,
        'logo',
        'images/logo1.png',
        1
    ),
    (
        2,
        'home_background',
        'images/homebg.jpg',
        1
    ),
    (
        3,
        'home_banner',
        'images/banner.jpg',
        1
    );
/*!40000 ALTER TABLE `site_assets` ENABLE KEYS */
;
UNLOCK TABLES;

--
-- Table structure for table `store_category`
--

DROP TABLE IF EXISTS `store_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!50503 SET character_set_client = utf8mb4 */
;
CREATE TABLE `store_category` (
    `id` bigint NOT NULL AUTO_INCREMENT,
    `name` varchar(100) NOT NULL,
    `description` longtext NOT NULL,
    `image` varchar(100) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;

--
-- Dumping data for table `store_category`
--

LOCK TABLES `store_category` WRITE;
/*!40000 ALTER TABLE `store_category` DISABLE KEYS */
;
/*!40000 ALTER TABLE `store_category` ENABLE KEYS */
;
UNLOCK TABLES;

--
-- Table structure for table `store_product`
--

DROP TABLE IF EXISTS `store_product`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!50503 SET character_set_client = utf8mb4 */
;
CREATE TABLE `store_product` (
    `id` bigint NOT NULL AUTO_INCREMENT,
    `name` varchar(200) NOT NULL,
    `description` longtext NOT NULL,
    `price` decimal(8, 2) NOT NULL,
    `image_url` varchar(200) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;

--
-- Dumping data for table `store_product`
--

LOCK TABLES `store_product` WRITE;
/*!40000 ALTER TABLE `store_product` DISABLE KEYS */
;
/*!40000 ALTER TABLE `store_product` ENABLE KEYS */
;
UNLOCK TABLES;

--
-- Table structure for table `subcategories`
--

DROP TABLE IF EXISTS `subcategories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!50503 SET character_set_client = utf8mb4 */
;
CREATE TABLE `subcategories` (
    `subcategory_id` int NOT NULL AUTO_INCREMENT,
    `subcategory_name` varchar(100) NOT NULL,
    `category_id` int NOT NULL,
    PRIMARY KEY (`subcategory_id`),
    KEY `category_id` (`category_id`),
    CONSTRAINT `subcategories_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`)
) ENGINE = InnoDB AUTO_INCREMENT = 12 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;

--
-- Dumping data for table `subcategories`
--

LOCK TABLES `subcategories` WRITE;
/*!40000 ALTER TABLE `subcategories` DISABLE KEYS */
;
INSERT INTO
    `subcategories`
VALUES (1, 'T-Shirts', 1),
    (2, 'Shirts', 1),
    (3, 'Jeans', 1),
    (4, 'Ethnic Wear', 2),
    (5, 'Western Wear', 2),
    (6, 'Footwear', 2),
    (7, 'Kids T-Shirts', 3),
    (8, 'Kids Dresses', 3),
    (9, 'Toys', 3),
    (11, 'Footwear', 3);
/*!40000 ALTER TABLE `subcategories` ENABLE KEYS */
;
UNLOCK TABLES;

--
-- Table structure for table `women_categories`
--

DROP TABLE IF EXISTS `women_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!50503 SET character_set_client = utf8mb4 */
;
CREATE TABLE `women_categories` (
    `women_category_id` int NOT NULL AUTO_INCREMENT,
    `category_id` int NOT NULL,
    `category_name` varchar(100) NOT NULL,
    `image` varchar(255) DEFAULT NULL,
    `description` text,
    `page_url` varchar(255) DEFAULT NULL,
    `is_active` tinyint(1) DEFAULT '1',
    `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`women_category_id`),
    KEY `fk_women_categories_category` (`category_id`),
    CONSTRAINT `fk_women_categories_category` FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`) ON DELETE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 5 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;

--
-- Dumping data for table `women_categories`
--

LOCK TABLES `women_categories` WRITE;
/*!40000 ALTER TABLE `women_categories` DISABLE KEYS */
;
INSERT INTO
    `women_categories`
VALUES (
        1,
        2,
        'Ethnic Wear',
        'images/women-ethnic.png',
        'Sarees, kurtis, and more.',
        '/womens_ethnicware',
        1,
        '2026-03-29 16:17:41'
    ),
    (
        2,
        2,
        'Western Wear',
        'images/women-western.png',
        'Dresses, tops, and more.',
        '/womens_westernware',
        1,
        '2026-03-29 16:17:41'
    ),
    (
        3,
        2,
        'Footwear',
        'images/women-footwear1.png',
        'Heels, flats, sneakers.',
        '/womens_footwear',
        1,
        '2026-03-29 16:17:41'
    ),
    (
        4,
        2,
        'Bags & Accessories',
        'images/women-bags.png',
        'Stylish & trendy picks.',
        '/accessories_women',
        1,
        '2026-03-29 16:17:41'
    );
/*!40000 ALTER TABLE `women_categories` ENABLE KEYS */
;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */
;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */
;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */
;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */
;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */
;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */
;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */
;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */
;

-- Dump completed on 2026-04-02 12:05:06