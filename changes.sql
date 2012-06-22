-- 2012-06-21

ALTER TABLE `brew_recipe` ADD `modified` datetime;
UPDATE `brew_recipe` SET `modified`= "2012-06-21 09:00:00";
ALTER TABLE `brew_recipe` change `modified` `modified` datetime NOT NULL;
