import { createClient } from "@supabase/supabase-js";
import dotenv from "dotenv";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseKey = import.meta.env.VITE_SUPABASE_API;

const supabase = createClient(supabaseUrl, supabaseKey);

export default supabase;