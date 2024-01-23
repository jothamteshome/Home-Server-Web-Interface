CREATE TABLE IF NOT EXISTS `returnData` (
`searchName`        varbinary(100) NOT NULL                   COMMENT 'The name to search for data with',
`itemName`          varbinary(100) NOT NULL            		  COMMENT 'The name of the item',
`itemSource`        varbinary(512) NOT NULL                   COMMENT 'The source location',
`itemProcessURL`    varbinary(100) NOT NULL                   COMMENT 'The url to process this data',
`itemDirName`       varbinary(512)                            COMMENT 'The location of the search directory for this content',
`itemThumb`         varbinary(512)                            COMMENT 'The source of the thumbnail',
PRIMARY KEY (`searchName`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Contains site user information";