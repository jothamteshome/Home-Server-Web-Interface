CREATE TABLE IF NOT EXISTS `uploadSourceDirectories` (
`source_dir_id`             int(11)           NOT NULL AUTO_INCREMENT     COMMENT 'ID of database entry',
`search_dir_name`           varbinary(64)     NOT NULL     		          COMMENT 'The name of the upload search directory',
`source_dir_name`           varbinary(64)     NOT NULL                    COMMENT 'The search directory location to upload to',
PRIMARY KEY (`source_dir_id`),
UNIQUE KEY `unique_pairs`(`search_dir_name`, `source_dir_name`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Matches search directories with source directories contained within them";