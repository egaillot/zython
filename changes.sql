-- 2012-11-02
ALTER TABLE `brew_recipehop` change `amount` `amount` numeric(6, 2) NOT NULL;

-- before
ALTER TABLE `brew_recipemalt` change `color` `color` numeric(7, 1) NOT NULL;


-- 2012-06-21
ALTER TABLE `brew_recipe` ADD `modified` datetime;
UPDATE `brew_recipe` SET `modified`= "2012-06-21 09:00:00";
ALTER TABLE `brew_recipe` change `modified` `modified` datetime NOT NULL;
