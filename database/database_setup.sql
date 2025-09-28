-- -- ==== DATABASE: MoMo Analytics (MySQL) ====

create table Transaction_Categories
(
    category_id   int auto_increment primary key,
    category_name varchar(100)                       not null,
    description   text                               null,
    created_at    datetime default CURRENT_TIMESTAMP null
);

create table Users
(
    user_id      int auto_increment
        primary key,
    full_name    varchar(150)                                                  not null,
    phone_number varchar(20)                                                   not null,
    email        varchar(100)                                                  null,
    national_id  varchar(30)                                                   not null,
    user_type    enum ('Customer', 'Agent', 'Admin') default 'Customer'        null,
    created_at   datetime                            default CURRENT_TIMESTAMP null,
    updated_at   datetime                            default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP,
    constraint email
        unique (email),
    constraint national_id
        unique (national_id),
    constraint phone_number
        unique (phone_number)
);

create table System_Logs
(
    log_id     int auto_increment
        primary key,
    user_id    int                                null,
    action     varchar(255)                       not null,
    details    text                               null,
    ip_address varchar(45)                        null,
    log_date   datetime default CURRENT_TIMESTAMP null,
    constraint System_Logs_ibfk_1
        foreign key (user_id) references Users (user_id)
            on delete set null
);

create index user_id
    on System_Logs (user_id);

create table Transactions
(
    transaction_id int auto_increment
        primary key,
    sender_id      int not null,
    receiver_id    int not null,
    category_id    int not null,
    amount         decimal(12, 2) not null,
    status         enum ('Pending', 'Completed', 'Failed', 'Reversed') default 'Pending'         null,
    created_at     datetime                                            default CURRENT_TIMESTAMP null,
    constraint Transactions_ibfk_1
        foreign key (sender_id) references Users (user_id),
    constraint Transactions_ibfk_2
        foreign key (receiver_id) references Users (user_id),
    constraint Transactions_ibfk_3
        foreign key (category_id) references Transaction_Categories (category_id)
);

create index category_id
    on Transactions (category_id);

create index receiver_id
    on Transactions (receiver_id);

create index sender_id
    on Transactions (sender_id);


