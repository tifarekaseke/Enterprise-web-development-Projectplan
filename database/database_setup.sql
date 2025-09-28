-- ==== DATABASE: MoMo Analytics (MySQL) ====

-- USERS / CUSTOMERS
CREATE TABLE users (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  msisdn        VARCHAR(20) NOT NULL UNIQUE COMMENT 'Phone in international format',
  name          VARCHAR(100) NULL,
  network       VARCHAR(30)  NULL,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) COMMENT='Unique participants found in SMS';

-- CATEGORIES
CREATE TABLE transaction_categories (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name        VARCHAR(40) NOT NULL UNIQUE,
  rule_hint   VARCHAR(200) NULL,
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) COMMENT='Business-defined transaction types';

-- TRANSACTIONS
CREATE TABLE transactions (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  occurred_at   DATETIME NOT NULL COMMENT 'Parsed timestamp from SMS',
  amount        DECIMAL(14,2) NOT NULL CHECK (amount >= 0),
  currency      CHAR(3) NOT NULL DEFAULT 'RWF',
  raw_text      TEXT NOT NULL,
  source_file   VARCHAR(255) NULL,
  ingested_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  sender_id     BIGINT NOT NULL,
  receiver_id   BIGINT NULL,
  category_id   INT    NULL,

  CONSTRAINT fk_tx_sender   FOREIGN KEY (sender_id)  REFERENCES users(id),
  CONSTRAINT fk_tx_receiver FOREIGN KEY (receiver_id)REFERENCES users(id),
  CONSTRAINT fk_tx_cat      FOREIGN KEY (category_id)REFERENCES transaction_categories(id)
) COMMENT='One row per accepted transaction';

-- OPTIONAL: M:N tagging (only if we model multiple labels)
CREATE TABLE transaction_tags (
  tx_id  BIGINT NOT NULL,
  tag_id INT    NOT NULL,
  PRIMARY KEY (tx_id, tag_id),
  FOREIGN KEY (tx_id)  REFERENCES transactions(id),
  FOREIGN KEY (tag_id) REFERENCES transaction_categories(id)
);

-- LOGS
CREATE TABLE system_logs (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  event_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  stage      ENUM('PARSE','CLEAN','CATEGORIZE','LOAD') NOT NULL,
  status     ENUM('INFO','WARN','ERROR') NOT NULL,
  detail     TEXT NULL,
  tx_id      BIGINT NULL,
  FOREIGN KEY (tx_id) REFERENCES transactions(id)
) COMMENT='ETL processing audit';

-- INDEXES (adjust to your queries)
CREATE INDEX idx_tx_time      ON transactions(occurred_at);
CREATE INDEX idx_tx_cat       ON transactions(category_id);
CREATE INDEX idx_tx_sender    ON transactions(sender_id);
CREATE INDEX idx_user_msisdn  ON users(msisdn);



