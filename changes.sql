
-- 2015-09-25
ALTER TABLE "brew_malt" ADD "stock_user_id" integer REFERENCES "auth_user" ("id");
ALTER TABLE "brew_malt" ADD "stock_added" datetime;
ALTER TABLE "brew_malt" ADD "stock_amount" decimal;

ALTER TABLE "brew_hop" ADD "stock_user_id" integer REFERENCES "auth_user" ("id");
ALTER TABLE "brew_hop" ADD "stock_added" datetime;
ALTER TABLE "brew_hop" ADD "stock_amount" decimal;

ALTER TABLE "brew_yeast" ADD "stock_user_id" integer REFERENCES "auth_user" ("id");
ALTER TABLE "brew_yeast" ADD "stock_added" datetime;
ALTER TABLE "brew_yeast" ADD "stock_amount" integer;




-- 2012-12-26
ALTER TABLE `brew_recipe` ADD `modified_by_id` integer;
CREATE INDEX `brew_recipe_6162aa58` ON `brew_recipe` (`modified_by_id`);


-- 2012-11-20
ALTER TABLE `brew_recipemisc` change `amount` `amount` numeric(10, 2) NOT NULL;
ALTER TABLE `brew_recipemisc` change `time` `time` numeric(10, 2) NOT NULL;

-- 2012-11-02
ALTER TABLE `brew_recipehop` change `amount` `amount` numeric(6, 2) NOT NULL;

-- before
ALTER TABLE `brew_recipemalt` change `color` `color` numeric(7, 1) NOT NULL;


-- 2012-06-21
ALTER TABLE `brew_recipe` ADD `modified` datetime;
UPDATE `brew_recipe` SET `modified`= "2012-06-21 09:00:00";
ALTER TABLE `brew_recipe` change `modified` `modified` datetime NOT NULL;
