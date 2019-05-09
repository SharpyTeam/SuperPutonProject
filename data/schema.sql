/* Тут находятся запросы, создающие структуру БД */

create table if not exists reports
(
    company_id  integer not null,
    period      text    not null,
    string_code text    not null,
    col_0       real default 0,
    col_1       real default 0,
    col_2       real default 0,
    col_3       real default 0,
    col_4       real default 0,
    col_5       real default 0,
    col_6       real default 0,
    col_7       real default 0,
    col_8       real default 0,
    col_9       real default 0,
    primary key (company_id, period, string_code)
);

create table if not exists available_periods
(
    year text not null primary key
);

create unique index available_periods_year_uindex
    on available_periods (year);

create table if not exists companies
(
    company_id   integer not null
        primary key,
    company_name text    not null
);

create unique index companies_company_id_uindex
    on companies (company_id);

create unique index companies_company_name_uindex
    on companies (company_name);

