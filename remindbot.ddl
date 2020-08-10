-- Create the database
CREATE DATABASE `calendar_app`;

USE `calendar_app`;
-- Create the table
CREATE TABLE `phone_numbers` (
  `id` varchar(25) NOT NULL DEFAULT '',
  `credentials` varchar(2048) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;