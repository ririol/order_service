
CREATE FUNCTION public.set_date_on_update() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_date = date_trunc('second', timezone('utc', now()));
    RETURN NEW;
END;
$$;
ALTER FUNCTION public.set_date_on_update() OWNER TO postgres;


CREATE FUNCTION public.update_item_updated_date() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE public."order"
    SET updated_date = date_trunc('second', timezone('utc', now()))
    WHERE id = NEW.order_id;
    RETURN NEW;
END;
$$;
ALTER FUNCTION public.update_item_updated_date() OWNER TO postgres;


CREATE FUNCTION public.update_order_total() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE public."order" o
    SET total = (
        SELECT COALESCE(SUM(price * "number"), 0)
        FROM public.item i
        WHERE i.order_id = o.id
    );
    RETURN NULL;
END;
$$;
ALTER FUNCTION public.update_order_total() OWNER TO postgres;



CREATE FUNCTION public.update_order_updated_date() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_date = date_trunc('second', timezone('utc', now()));
    RETURN NEW;
END;
$$;
ALTER FUNCTION public.update_order_updated_date() OWNER TO postgres;


SET default_tablespace = '';

SET default_table_access_method = heap;


CREATE TABLE public.item (
    id integer NOT NULL,
    name character varying NOT NULL,
    price integer NOT NULL,
    number integer NOT NULL,
    order_id integer NOT NULL
);


ALTER TABLE public.item OWNER TO postgres;


CREATE SEQUENCE public.item_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.item_id_seq OWNER TO postgres;

ALTER SEQUENCE public.item_id_seq OWNED BY public.item.id;

CREATE TABLE public."order" (
    id integer NOT NULL,
    created_date timestamp without time zone DEFAULT date_trunc('second'::text, timezone('utc'::text, now())),
    updated_date timestamp without time zone DEFAULT date_trunc('second'::text, timezone('utc'::text, now())),
    title character varying,
    total integer DEFAULT 0
);


ALTER TABLE public."order" OWNER TO postgres;

CREATE SEQUENCE public.order_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.order_id_seq OWNER TO postgres;

ALTER SEQUENCE public.order_id_seq OWNED BY public."order".id;


ALTER TABLE ONLY public.item ALTER COLUMN id SET DEFAULT nextval('public.item_id_seq'::regclass);

ALTER TABLE ONLY public."order" ALTER COLUMN id SET DEFAULT nextval('public.order_id_seq'::regclass);

SELECT pg_catalog.setval('public.item_id_seq', 1, true);

SELECT pg_catalog.setval('public.order_id_seq', 1, true);

ALTER TABLE ONLY public.item
    ADD CONSTRAINT item_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public."order"
    ADD CONSTRAINT order_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.item
    ADD CONSTRAINT unique_item UNIQUE (name, price, order_id);

CREATE TRIGGER item_update_total_trigger AFTER INSERT OR DELETE OR UPDATE ON public.item FOR EACH ROW EXECUTE FUNCTION public.update_order_total();

CREATE TRIGGER item_update_trigger AFTER INSERT OR UPDATE ON public.item FOR EACH ROW EXECUTE FUNCTION public.update_item_updated_date();

CREATE TRIGGER order_update_trigger BEFORE UPDATE ON public."order" FOR EACH ROW EXECUTE FUNCTION public.update_order_updated_date();

ALTER TABLE ONLY public.item
    ADD CONSTRAINT item_order_id_fkey FOREIGN KEY (order_id) REFERENCES public."order"(id) ON DELETE CASCADE;
