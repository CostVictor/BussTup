-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema busstup
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema busstup
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `busstup` DEFAULT CHARACTER SET utf8 ;
USE `busstup` ;

-- -----------------------------------------------------
-- Table `busstup`.`aluno`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `busstup`.`aluno` (
  `id` BIGINT(20) NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) NOT NULL,
  `curso` VARCHAR(25) NOT NULL,
  `turno` ENUM('Matutino', 'Vespertino', 'Noturno') NOT NULL,
  `telefone` CHAR(15) NOT NULL,
  `email` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `busstup`.`linha`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `busstup`.`linha` (
  `codigo` INT(11) NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) NOT NULL,
  `cidade` VARCHAR(100) NOT NULL,
  `paga` TINYINT(4) NOT NULL,
  `ferias` TINYINT(4) NOT NULL DEFAULT 0,
  `valor_cartela` DECIMAL(5,2) NULL DEFAULT NULL,
  `valor_diaria` DECIMAL(4,2) NULL DEFAULT NULL,
  PRIMARY KEY (`codigo`),
  UNIQUE INDEX `nome_UNIQUE` (`nome` ASC))
ENGINE = InnoDB
AUTO_INCREMENT = 3
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `busstup`.`motorista`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `busstup`.`motorista` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) NOT NULL,
  `email` VARCHAR(100) NOT NULL,
  `telefone` CHAR(15) NOT NULL,
  `pix` VARCHAR(100) NULL DEFAULT 'Não definido',
  PRIMARY KEY (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `busstup`.`onibus`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `busstup`.`onibus` (
  `id` BIGINT(20) NOT NULL AUTO_INCREMENT,
  `apelido` VARCHAR(15) NOT NULL,
  `capacidade` INT(11) NOT NULL,
  `Linha_codigo` INT(11) NOT NULL,
  `Motorista_id` INT(11) NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_Onibus_Motorista1_idx` (`Motorista_id` ASC),
  INDEX `fk_Onibus_Linha1_idx` (`Linha_codigo` ASC),
  CONSTRAINT `fk_Onibus_Linha1`
    FOREIGN KEY (`Linha_codigo`)
    REFERENCES `busstup`.`linha` (`codigo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Onibus_Motorista1`
    FOREIGN KEY (`Motorista_id`)
    REFERENCES `busstup`.`motorista` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 3
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `busstup`.`aparencia`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `busstup`.`aparencia` (
  `Onibus_id` BIGINT(20) NOT NULL,
  `cor` VARCHAR(50) NOT NULL,
  `modelo` VARCHAR(50) NOT NULL,
  `descricao` VARCHAR(255) NOT NULL DEFAULT 'Não definido',
  PRIMARY KEY (`Onibus_id`),
  INDEX `fk_Aparencia_Onibus1_idx` (`Onibus_id` ASC),
  CONSTRAINT `fk_Aparencia_Onibus1`
    FOREIGN KEY (`Onibus_id`)
    REFERENCES `busstup`.`onibus` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `busstup`.`cartela_ticket`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `busstup`.`cartela_ticket` (
  `id` BIGINT(20) NOT NULL AUTO_INCREMENT,
  `valida` TINYINT(4) NOT NULL DEFAULT 1,
  `data_expiracao` DATE NOT NULL,
  `data_adicao` DATE NOT NULL,
  `quantidade` INT(11) NOT NULL,
  `ultima_atualizacao` DATE NULL DEFAULT NULL,
  `Linha_codigo` INT(11) NOT NULL,
  `Aluno_id` BIGINT(20) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_Cartela_Ticket_Linha1_idx` (`Linha_codigo` ASC),
  INDEX `fk_Cartela_Ticket_Aluno1_idx` (`Aluno_id` ASC),
  CONSTRAINT `fk_Cartela_Ticket_Aluno1`
    FOREIGN KEY (`Aluno_id`)
    REFERENCES `busstup`.`aluno` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Cartela_Ticket_Linha1`
    FOREIGN KEY (`Linha_codigo`)
    REFERENCES `busstup`.`linha` (`codigo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `busstup`.`contraturno_fixo`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `busstup`.`contraturno_fixo` (
  `id` BIGINT(20) NOT NULL AUTO_INCREMENT,
  `dia_fixo` INT NOT NULL CHECK(`dia_fixo` IN (0, 1, 2, 3, 4)),
  `Aluno_id` BIGINT(20) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_Contraturno_Fixo_Aluno1_idx` (`Aluno_id` ASC),
  CONSTRAINT `fk_Contraturno_Fixo_Aluno1`
    FOREIGN KEY (`Aluno_id`)
    REFERENCES `busstup`.`aluno` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `busstup`.`marcador_exclusao`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `busstup`.`marcador_exclusao` (
  `id` BIGINT(20) NOT NULL AUTO_INCREMENT,
  `tabela` VARCHAR(20) NOT NULL,
  `key_item` BIGINT(20) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `busstup`.`membro`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `busstup`.`membro` (
  `Linha_codigo` INT(11) NOT NULL,
  `Motorista_id` INT(11) NOT NULL,
  `dono` TINYINT(4) NOT NULL DEFAULT 0,
  `adm` TINYINT(4) NOT NULL DEFAULT 0,
  PRIMARY KEY (`Linha_codigo`, `Motorista_id`),
  INDEX `fk_Membro_Motorista1_idx` (`Motorista_id` ASC),
  INDEX `fk_Membro_Linha1_idx` (`Linha_codigo` ASC),
  CONSTRAINT `fk_Membro_Linha1`
    FOREIGN KEY (`Linha_codigo`)
    REFERENCES `busstup`.`linha` (`codigo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Membro_Motorista1`
    FOREIGN KEY (`Motorista_id`)
    REFERENCES `busstup`.`motorista` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `busstup`.`ponto`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `busstup`.`ponto` (
  `id` BIGINT(20) NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) NOT NULL,
  `tempo_tolerancia` VARCHAR(2) NOT NULL DEFAULT '5',
  `linkGPS` VARCHAR(200) NULL DEFAULT NULL,
  `Linha_codigo` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_Ponto_Linha1_idx` (`Linha_codigo` ASC),
  CONSTRAINT `fk_Ponto_Linha1`
    FOREIGN KEY (`Linha_codigo`)
    REFERENCES `busstup`.`linha` (`codigo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `busstup`.`rota`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `busstup`.`rota` (
  `codigo` BIGINT(20) NOT NULL AUTO_INCREMENT,
  `turno` ENUM('Matutino', 'Vespertino', 'Noturno') NOT NULL,
  `em_partida` TINYINT(4) NOT NULL DEFAULT 0,
  `em_retorno` TINYINT(4) NOT NULL DEFAULT 0,
  `horario_partida` TIME NOT NULL,
  `horario_retorno` TIME NOT NULL,
  `Linha_codigo` INT(11) NOT NULL,
  `Onibus_id` BIGINT(20) NULL,
  PRIMARY KEY (`codigo`),
  INDEX `fk_Rota_Linha1_idx` (`Linha_codigo` ASC),
  INDEX `fk_Rota_Onibus1_idx` (`Onibus_id` ASC),
  CONSTRAINT `fk_Rota_Linha1`
    FOREIGN KEY (`Linha_codigo`)
    REFERENCES `busstup`.`linha` (`codigo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Rota_Onibus1`
    FOREIGN KEY (`Onibus_id`)
    REFERENCES `busstup`.`onibus` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 4
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `busstup`.`parada`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `busstup`.`parada` (
  `codigo` BIGINT(20) NOT NULL AUTO_INCREMENT,
  `tipo` ENUM('partida', 'retorno') NOT NULL,
  `ordem` INT(11) NOT NULL,
  `horario_passagem` TIME NOT NULL,
  `Rota_codigo` BIGINT(20) NOT NULL,
  `Ponto_id` BIGINT(20) NOT NULL,
  PRIMARY KEY (`codigo`),
  INDEX `fk_Parada_Rota1_idx` (`Rota_codigo` ASC),
  INDEX `fk_Parada_Ponto1_idx` (`Ponto_id` ASC),
  CONSTRAINT `fk_Parada_Ponto1`
    FOREIGN KEY (`Ponto_id`)
    REFERENCES `busstup`.`ponto` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Parada_Rota1`
    FOREIGN KEY (`Rota_codigo`)
    REFERENCES `busstup`.`rota` (`codigo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 5
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `busstup`.`passagem`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `busstup`.`passagem` (
  `codigo` BIGINT(20) NOT NULL AUTO_INCREMENT,
  `passagem_fixa` TINYINT(4) NOT NULL,
  `passagem_contraturno` TINYINT(4) NOT NULL,
  `migracao_lotado` TINYINT NOT NULL DEFAULT 0,
  `migracao_manutencao` TINYINT NOT NULL DEFAULT 0,
  `pediu_espera` TINYINT(4) NOT NULL DEFAULT 0,
  `data` DATE NULL DEFAULT NULL,
  `Parada_codigo` BIGINT(20) NOT NULL,
  `Aluno_id` BIGINT(20) NOT NULL,
  PRIMARY KEY (`codigo`),
  INDEX `fk_Passagem_Parada1_idx` (`Parada_codigo` ASC),
  INDEX `fk_Passagem_Aluno1_idx` (`Aluno_id` ASC),
  CONSTRAINT `fk_Passagem_Aluno1`
    FOREIGN KEY (`Aluno_id`)
    REFERENCES `busstup`.`aluno` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Passagem_Parada1`
    FOREIGN KEY (`Parada_codigo`)
    REFERENCES `busstup`.`parada` (`codigo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 11
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `busstup`.`registro_aluno`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `busstup`.`registro_aluno` (
  `codigo` BIGINT(20) NOT NULL AUTO_INCREMENT,
  `data` DATE NOT NULL,
  `faltara` TINYINT(4) NOT NULL DEFAULT 0,
  `contraturno` TINYINT(4) NOT NULL DEFAULT 0,
  `presente_partida` TINYINT(4) NOT NULL DEFAULT 0,
  `presente_retorno` TINYINT(4) NOT NULL DEFAULT 0,
  `Aluno_id` BIGINT(20) NOT NULL,
  PRIMARY KEY (`codigo`),
  INDEX `fk_Registro_Aluno_Aluno1_idx` (`Aluno_id` ASC),
  CONSTRAINT `fk_Registro_Aluno_Aluno1`
    FOREIGN KEY (`Aluno_id`)
    REFERENCES `busstup`.`aluno` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `busstup`.`registro_passagem`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `busstup`.`registro_passagem` (
  `codigo` BIGINT(20) NOT NULL AUTO_INCREMENT,
  `data` DATETIME NOT NULL,
  `Parada_codigo` BIGINT(20) NOT NULL,
  PRIMARY KEY (`codigo`),
  INDEX `fk_Registro_Parada_Parada1_idx` (`Parada_codigo` ASC),
  CONSTRAINT `fk_Registro_Parada_Parada1`
    FOREIGN KEY (`Parada_codigo`)
    REFERENCES `busstup`.`parada` (`codigo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `busstup`.`registro_rota`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `busstup`.`registro_rota` (
  `codigo` BIGINT(20) NOT NULL AUTO_INCREMENT,
  `data` DATE NOT NULL,
  `tipo` ENUM('partida', 'retorno') NOT NULL,
  `quantidade_pessoas` INT(11) NOT NULL DEFAULT 0,
  `previsao_pessoas` INT(11) NOT NULL DEFAULT 0,
  `atualizar` TINYINT NOT NULL DEFAULT 0,
  `Rota_codigo` BIGINT(20) NOT NULL,
  PRIMARY KEY (`codigo`),
  INDEX `fk_Registro_Rota_Rota1_idx` (`Rota_codigo` ASC),
  CONSTRAINT `fk_Registro_Rota_Rota1`
    FOREIGN KEY (`Rota_codigo`)
    REFERENCES `busstup`.`rota` (`codigo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `busstup`.`manutencao`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `busstup`.`manutencao` (
  `codigo` BIGINT NOT NULL AUTO_INCREMENT,
  `data_inicio` DATETIME NOT NULL,
  `data_fim` DATETIME NOT NULL,
  `onibus_id` BIGINT(20) NOT NULL,
  PRIMARY KEY (`codigo`),
  INDEX `fk_manutencao_onibus1_idx` (`onibus_id` ASC),
  CONSTRAINT `fk_manutencao_onibus1`
    FOREIGN KEY (`onibus_id`)
    REFERENCES `busstup`.`onibus` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `busstup`.`registro_linha`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `busstup`.`registro_linha` (
  `codigo` BIGINT NOT NULL AUTO_INCREMENT,
  `funcionamento` TINYINT NOT NULL DEFAULT 1,
  `feriado` TINYINT NOT NULL DEFAULT 0,
  `data` DATE NOT NULL,
  `linha_codigo` INT(11) NOT NULL,
  PRIMARY KEY (`codigo`),
  INDEX `fk_calendario_linha1_idx` (`linha_codigo` ASC),
  CONSTRAINT `fk_calendario_linha1`
    FOREIGN KEY (`linha_codigo`)
    REFERENCES `busstup`.`linha` (`codigo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
