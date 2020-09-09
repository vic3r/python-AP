
--- CREATE order_lines
CREATE TABLE public.order_lines
(
    id serial NOT NULL,
    sku character varying(255) COLLATE pg_catalog."default",
    qty integer NOT NULL,
    orderid character varying(255) COLLATE pg_catalog."default",
    CONSTRAINT orderline_id PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.order_lines
    OWNER to allocation;

--- CREATE batches
CREATE TABLE public.batches
(
    id serial NOT NULL,
	reference character varying(255) COLLATE pg_catalog."default",
    sku character varying(255) COLLATE pg_catalog."default",
    _purchased_quantity integer NOT NULL,
    eta date NOT NULL,
    CONSTRAINT batch_id PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.batches
    OWNER to allocation;

--- CREATE allocations
CREATE TABLE public.allocations
(
    id integer NOT NULL DEFAULT nextval('allocations_id_seq'::regclass),
    orderline_id integer NOT NULL,
    batch_id integer NOT NULL,
    CONSTRAINT allocation_id PRIMARY KEY (id),
    CONSTRAINT batch_id_fk FOREIGN KEY (batch_id)
        REFERENCES public.batches (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT orderline_id_fk FOREIGN KEY (orderline_id)
        REFERENCES public.order_lines (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.allocations
    OWNER to allocation;
