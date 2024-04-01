-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema busstup_session
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema busstup_session
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `busstup_session` DEFAULT CHARACTER SET utf8 ;
USE `busstup_session` ;

-- -----------------------------------------------------
-- Table `busstup_session`.`User`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `busstup_session`.`User` (
  `id` BIGINT(20) NOT NULL AUTO_INCREMENT,
  `login` VARCHAR(100) NOT NULL,
  `password_hash` BINARY(60) NOT NULL,
  `primary_key` BIGINT(20) NOT NULL,
  `fs_uniquifier` VARCHAR(64) NOT NULL,
  `active` TINYINT(4) NOT NULL DEFAULT 1,
  `analysis` TINYINT(4) NOT NULL DEFAULT 0,
  `aceitou_termo_uso_dados` TINYINT(4) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `fs_uniquifier_UNIQUE` (`fs_uniquifier` ASC),
  UNIQUE INDEX `login_UNIQUE` (`login` ASC))
ENGINE = InnoDB
AUTO_INCREMENT = 6
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `busstup_session`.`Role`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `busstup_session`.`Role` (
  `id` BIGINT(20) NOT NULL AUTO_INCREMENT,
  `name` ENUM('aluno', 'motorista', 'administrador') NOT NULL,
  `User_id` BIGINT(20) NOT NULL,
  PRIMARY KEY (`id`, `User_id`),
  INDEX `fk_Role_User_idx` (`User_id` ASC),
  CONSTRAINT `fk_Role_User`
    FOREIGN KEY (`User_id`)
    REFERENCES `busstup_session`.`User` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 6
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `busstup_session`.`Contribuicao`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `busstup_session`.`Contribuicao` (
  `User_id` BIGINT(20) NOT NULL,
  PRIMARY KEY (`User_id`),
  CONSTRAINT `fk_Contribuicao_User1`
    FOREIGN KEY (`User_id`)
    REFERENCES `busstup_session`.`User` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `busstup_session`.`SendEmail`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `busstup_session`.`SendEmail` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `to` VARCHAR(255) NOT NULL,
  `type` ENUM('acesso', 'criar', 'recuperar') NOT NULL,
  `data` JSON NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `busstup_session`.`AccessToken`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `busstup_session`.`AccessToken` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `type` ENUM('recuperacao', 'confirmacao') NOT NULL DEFAULT 'recuperacao',
  `token` TEXT NOT NULL,
  `User_id` BIGINT(20) NOT NULL,
  PRIMARY KEY (`id`, `User_id`),
  INDEX `fk_AccessToken_User1_idx` (`User_id` ASC),
  UNIQUE INDEX `token_UNIQUE` (`token` ASC),
  CONSTRAINT `fk_AccessToken_User1`
    FOREIGN KEY (`User_id`)
    REFERENCES `busstup_session`.`User` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
