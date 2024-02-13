-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema Busstup
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema Busstup
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `Busstup` DEFAULT CHARACTER SET utf8 ;
USE `Busstup` ;

-- -----------------------------------------------------
-- Table `Busstup`.`Motorista`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Busstup`.`Motorista` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) NOT NULL,
  `email` VARCHAR(100) NOT NULL,
  `telefone` CHAR(15) NOT NULL,
  `pix` VARCHAR(100) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Busstup`.`Linha`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Busstup`.`Linha` (
  `codigo` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) NOT NULL,
  `cidade` VARCHAR(100) NOT NULL,
  `paga` TINYINT NOT NULL,
  `ferias` TINYINT NOT NULL DEFAULT 0,
  `valor_cartela` DECIMAL(5,2) NULL,
  `valor_diaria` DECIMAL(4,2) NULL,
  PRIMARY KEY (`codigo`),
  UNIQUE INDEX `nome_UNIQUE` (`nome` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Busstup`.`Onibus`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Busstup`.`Onibus` (
  `placa` CHAR(7) NOT NULL,
  `capacidade` INT NOT NULL,
  `Linha_codigo` INT NOT NULL,
  `Motorista_id` INT NULL,
  PRIMARY KEY (`placa`),
  INDEX `fk_Onibus_Motorista1_idx` (`Motorista_id` ASC),
  INDEX `fk_Onibus_Linha1_idx` (`Linha_codigo` ASC),
  CONSTRAINT `fk_Onibus_Motorista1`
    FOREIGN KEY (`Motorista_id`)
    REFERENCES `Busstup`.`Motorista` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Onibus_Linha1`
    FOREIGN KEY (`Linha_codigo`)
    REFERENCES `Busstup`.`Linha` (`codigo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Busstup`.`Rota`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Busstup`.`Rota` (
  `codigo` BIGINT NOT NULL AUTO_INCREMENT,
  `turno` ENUM('Matutino', 'Vespertino', 'Noturno') NOT NULL,
  `em_partida` TINYINT NOT NULL DEFAULT 0,
  `em_retorno` TINYINT NOT NULL DEFAULT 0,
  `horario_partida` TIME NOT NULL,
  `horario_retorno` TIME NOT NULL,
  `Linha_codigo` INT NOT NULL,
  `Onibus_placa` CHAR(7) NULL,
  PRIMARY KEY (`codigo`),
  INDEX `fk_Rota_Linha1_idx` (`Linha_codigo` ASC),
  INDEX `fk_Rota_Onibus1_idx` (`Onibus_placa` ASC),
  CONSTRAINT `fk_Rota_Linha1`
    FOREIGN KEY (`Linha_codigo`)
    REFERENCES `Busstup`.`Linha` (`codigo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Rota_Onibus1`
    FOREIGN KEY (`Onibus_placa`)
    REFERENCES `Busstup`.`Onibus` (`placa`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Busstup`.`Aluno`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Busstup`.`Aluno` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) NOT NULL,
  `curso` VARCHAR(25) NOT NULL,
  `turno` ENUM('Matutino', 'Vespertino', 'Noturno') NOT NULL,
  `telefone` CHAR(15) NOT NULL,
  `email` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Busstup`.`Registro_Aluno`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Busstup`.`Registro_Aluno` (
  `codigo` BIGINT NOT NULL AUTO_INCREMENT,
  `data` DATE NOT NULL,
  `faltara` TINYINT NOT NULL DEFAULT 0,
  `contraturno` TINYINT NOT NULL DEFAULT 0,
  `presente_partida` TINYINT NOT NULL DEFAULT 0,
  `presente_retorno` TINYINT NOT NULL DEFAULT 0,
  `Aluno_id` BIGINT NOT NULL,
  PRIMARY KEY (`codigo`),
  INDEX `fk_Registro_Aluno_Aluno1_idx` (`Aluno_id` ASC),
  CONSTRAINT `fk_Registro_Aluno_Aluno1`
    FOREIGN KEY (`Aluno_id`)
    REFERENCES `Busstup`.`Aluno` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Busstup`.`Ponto`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Busstup`.`Ponto` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) NOT NULL,
  `tempo_tolerancia` VARCHAR(2) NOT NULL DEFAULT '5',
  `linkGPS` VARCHAR(200) NULL,
  `Linha_codigo` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_Ponto_Linha1_idx` (`Linha_codigo` ASC),
  CONSTRAINT `fk_Ponto_Linha1`
    FOREIGN KEY (`Linha_codigo`)
    REFERENCES `Busstup`.`Linha` (`codigo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Busstup`.`Parada`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Busstup`.`Parada` (
  `codigo` BIGINT NOT NULL AUTO_INCREMENT,
  `tipo` ENUM('partida', 'retorno') NOT NULL,
  `ordem` INT NOT NULL,
  `horario_passagem` TIME NOT NULL,
  `Rota_codigo` BIGINT NOT NULL,
  `Ponto_id` BIGINT NOT NULL,
  PRIMARY KEY (`codigo`),
  INDEX `fk_Parada_Rota1_idx` (`Rota_codigo` ASC),
  INDEX `fk_Parada_Ponto1_idx` (`Ponto_id` ASC),
  CONSTRAINT `fk_Parada_Rota1`
    FOREIGN KEY (`Rota_codigo`)
    REFERENCES `Busstup`.`Rota` (`codigo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Parada_Ponto1`
    FOREIGN KEY (`Ponto_id`)
    REFERENCES `Busstup`.`Ponto` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Busstup`.`Cartela_Ticket`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Busstup`.`Cartela_Ticket` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `valida` TINYINT NOT NULL DEFAULT 1,
  `data_expiracao` DATE NOT NULL,
  `data_adicao` DATE NOT NULL,
  `quantidade` INT NOT NULL,
  `ultima_atualizacao` DATE NULL,
  `Linha_codigo` INT NOT NULL,
  `Aluno_id` BIGINT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_Cartela_Ticket_Linha1_idx` (`Linha_codigo` ASC),
  INDEX `fk_Cartela_Ticket_Aluno1_idx` (`Aluno_id` ASC),
  CONSTRAINT `fk_Cartela_Ticket_Linha1`
    FOREIGN KEY (`Linha_codigo`)
    REFERENCES `Busstup`.`Linha` (`codigo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Cartela_Ticket_Aluno1`
    FOREIGN KEY (`Aluno_id`)
    REFERENCES `Busstup`.`Aluno` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Busstup`.`Contraturno_Fixo`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Busstup`.`Contraturno_Fixo` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `dia_fixo` ENUM('Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta') NOT NULL,
  `Aluno_id` BIGINT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_Contraturno_Fixo_Aluno1_idx` (`Aluno_id` ASC),
  CONSTRAINT `fk_Contraturno_Fixo_Aluno1`
    FOREIGN KEY (`Aluno_id`)
    REFERENCES `Busstup`.`Aluno` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Busstup`.`Membro`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Busstup`.`Membro` (
  `Linha_codigo` INT NOT NULL,
  `Motorista_id` INT NOT NULL,
  `dono` TINYINT NOT NULL DEFAULT 0,
  `adm` TINYINT NOT NULL DEFAULT 0,
  PRIMARY KEY (`Linha_codigo`, `Motorista_id`),
  INDEX `fk_Membro_Motorista1_idx` (`Motorista_id` ASC),
  INDEX `fk_Membro_Linha1_idx` (`Linha_codigo` ASC),
  CONSTRAINT `fk_Membro_Motorista1`
    FOREIGN KEY (`Motorista_id`)
    REFERENCES `Busstup`.`Motorista` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Membro_Linha1`
    FOREIGN KEY (`Linha_codigo`)
    REFERENCES `Busstup`.`Linha` (`codigo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Busstup`.`Registro_Parada`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Busstup`.`Registro_Parada` (
  `codigo` BIGINT NOT NULL AUTO_INCREMENT,
  `data` DATE NOT NULL,
  `veiculo_passou` TINYINT NOT NULL DEFAULT 0,
  `quantidade_no_veiculo` INT NOT NULL,
  `Parada_codigo` BIGINT NOT NULL,
  PRIMARY KEY (`codigo`),
  INDEX `fk_Registro_Parada_Parada1_idx` (`Parada_codigo` ASC),
  CONSTRAINT `fk_Registro_Parada_Parada1`
    FOREIGN KEY (`Parada_codigo`)
    REFERENCES `Busstup`.`Parada` (`codigo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Busstup`.`Registro_Rota`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Busstup`.`Registro_Rota` (
  `codigo` BIGINT NOT NULL AUTO_INCREMENT,
  `data` DATE NOT NULL,
  `tipo` ENUM('partida', 'retorno') NOT NULL,
  `quantidade_pessoas` INT NOT NULL,
  `previsao_pessoas` INT NOT NULL,
  `Rota_codigo` BIGINT NOT NULL,
  PRIMARY KEY (`codigo`),
  INDEX `fk_Registro_Rota_Rota1_idx` (`Rota_codigo` ASC),
  CONSTRAINT `fk_Registro_Rota_Rota1`
    FOREIGN KEY (`Rota_codigo`)
    REFERENCES `Busstup`.`Rota` (`codigo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Busstup`.`Passagem`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Busstup`.`Passagem` (
  `codigo` BIGINT NOT NULL AUTO_INCREMENT,
  `passagem_fixa` TINYINT NOT NULL,
  `passagem_contraturno` TINYINT NOT NULL,
  `pediu_espera` TINYINT NOT NULL DEFAULT 0,
  `data` DATE NULL,
  `Parada_codigo` BIGINT NOT NULL,
  `Aluno_id` BIGINT NOT NULL,
  PRIMARY KEY (`codigo`),
  INDEX `fk_Passagem_Parada1_idx` (`Parada_codigo` ASC),
  INDEX `fk_Passagem_Aluno1_idx` (`Aluno_id` ASC),
  CONSTRAINT `fk_Passagem_Parada1`
    FOREIGN KEY (`Parada_codigo`)
    REFERENCES `Busstup`.`Parada` (`codigo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Passagem_Aluno1`
    FOREIGN KEY (`Aluno_id`)
    REFERENCES `Busstup`.`Aluno` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
