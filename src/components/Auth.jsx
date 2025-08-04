import { useState, useRef, useEffect } from "react";
import supabase from "./supabaseClient";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTimes, faArrowLeft } from "@fortawesome/free-solid-svg-icons";
import "./Auth.css";
import PropTypes from "prop-types";
import { ThreeCircles } from "react-loader-spinner";
import { useLocation, useNavigate } from "react-router-dom";



export default function Auth(props) {
    // all variables and hooks
    const navigate = useNavigate(); // For navigation
    const location = useLocation(); // Get location state
    const { from } = location.state || { from: { pathname: "/" } }; // Default to homepage
    // const element = <FontAwesomeIcon icon={faTimes} />; 
    const element01 = <FontAwesomeIcon icon={faArrowLeft} size="xl" />
    const [loading, setLoading] = useState(false);
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [isSignUp, setIsSignUp] = useState(false);
    const [error, setError] = useState(null);
    const [back, setBack] = useState(false);



    useEffect(() => {
        /* Save the current route to localStorage before login
        const originalRoute = location.pathname; */
        localStorage.setItem("redirectAfterLogin", from.pathname);
    }, [from]);

    const spinner = (
        <ThreeCircles
            visible={true}
            height="20"
            width="20"
            color="white"
            ariaLabel="three-circles-loading"
            wrapperStyle={{}}
            wrapperClass=""
        />
    );

    // to close authenticate component
    // const clsfunc = () => {
    //     props.handle(false);
    // };
    // button reference
    // const buttonref = useRef();

    // hiding cls button
    // const hide = props.hideBtn;
    // useEffect(() => {
    //     if (hide) {
    //         buttonref.current.style.display = "none";
    //     }
    // }, [hide]);


    // const handleAuth = async (e) => {
    //     e.preventDefault();
    //     setLoading(true);
    //     setError(null);

    //     try {
    //         const { error } = await supabase.auth.signInWithPassword({
    //             email,
    //             password,
    //         });
    //         if (error) throw error;

    //         // Get the original route from localStorage
    //         const redirectAfterLogin =
    //             localStorage.getItem("redirectAfterLogin") || "/";
    //         // Clean up
    //         navigate(redirectAfterLogin); // Redirect to original route

    //     } catch (error) {
    //         setError(error.message || "An error occurred");
    //     } finally {
    //         setLoading(false);
    //     }
    // };

    const handleAuth = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        console.log("email", email)
        console.log("pass", password);
        

        try {
            if (!email || !password) {
                throw new Error("Email and password are required");
            }

            let response;
            if (isSignUp) {
                // Sign up logic
                response = await supabase.auth.signUp({
                    email,
                    password,
                });
            } else {
                // Sign in logic
                response = await supabase.auth.signInWithPassword({
                    email,
                    password,
                });
            }
    
            if (response.error) throw response.error;

            // Get the original route from localStorage
            const redirectAfterLogin =
                localStorage.getItem("redirectAfterLogin") || "/";
            localStorage.removeItem("redirectAfterLogin");
             // Clean up
            navigate(redirectAfterLogin); // Redirect to original route

        } catch (error) {
            setError(error.message || "An error occurred");
        } finally {
            setLoading(false);
        }
    };


    const handleOAuth = async (provider) => {
        
        try {
            localStorage.setItem("redirectAfterLogin", from.pathname); // Save route

            // Store the redirect URL
            const redirectAfterLogin =
                localStorage.getItem("redirectAfterLogin") ?? null;
            localStorage.removeItem("redirectAfterLogin"); //clean up
            const { error } = await supabase.auth.signInWithOAuth({
                provider,
                options: {
                    redirectTo: `${window.location.origin}${redirectAfterLogin}`, // Redirect after login
                },
            });            

            if (error) throw error;
        } catch (error) {
            setError(error.message || "An error occurred during OAuth login");
        }
    };

    const backButtonref = useRef();
    useEffect(() => {
        if (back) {
            navigate(from.pathname || localStorage.getItem('redirectAfterLogin'));
        }
    }, [back])


    return (
        <div className="auth-container">
            <div className="auth-box">
                {/* close button
                <button
                    className="clsbtn"
                    id="btnfinal"
                    ref={buttonref}
                    onClick={clsfunc}
                >
                    {element}
                </button> */}
                <button className="back-button"
                    ref={backButtonref}
                    onClick={() => {
                        setBack(!back);
                    }}>
                    {element01}
                </button>
                <h2 className="auth-title">
                    {/* title for authentication component */}
                    {isSignUp ? "Create your account" : "Sign in to your account"}
                </h2>
                {/* form  */}
                <form className="auth-form" onSubmit={handleAuth}>
                    <div className="form-group">
                        <label htmlFor="email">Email address</label>
                        <input
                            id="email"
                            name="email"
                            type="email"
                            autoComplete="email"
                            required
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <input
                            id="password"
                            name="password"
                            type="password"
                            autoComplete="current-password"
                            required
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </div>
                    {/* displaying error */}
                    {error && <div className="error-message">{error}</div>}
                    {/* button for submition */}
                    <button type="submit" disabled={loading} className="submit-button">
                        {loading ? spinner : isSignUp ? "Sign up" : "Sign in"}
                    </button>
                </form>

                <div className="divider">
                    <span>Or continue with</span>
                </div>

                <div className="oauth-buttons">
                    <button
                        onClick={(e) => handleOAuth("google", e)}
                        className="oauth-button"
                    >
                        <span className="sr-only">Sign in with Google</span>
                        <svg className="oauth-icon" viewBox="0 0 24 24">
                            <path
                                fill="currentColor"
                                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                            />
                            <path
                                fill="currentColor"
                                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                            />
                            <path
                                fill="currentColor"
                                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                            />
                            <path
                                fill="currentColor"
                                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                            />
                        </svg>
                    </button>
                    <button
                        onClick={(e) => handleOAuth("facebook", e)}
                        className="oauth-button"
                    >
                        <span className="sr-only">Sign in with Facebook</span>
                        <svg className="oauth-icon" viewBox="0 0 24 24">
                            <path
                                fill="currentColor"
                                d="M22.68 0H1.32C.59 0 0 .59 0 1.32v21.36C0 23.41.59 24 1.32 24h11.5v-9.3H9.69v-3.62h3.13V8.41c0-3.1 1.89-4.79 4.66-4.79 1.32 0 2.46.1 2.79.14v3.24h-1.92c-1.5 0-1.79.71-1.79 1.76v2.31h3.58l-.47 3.62h-3.11V24h6.12c.73 0 1.32-.59 1.32-1.32V1.32C24 .59 23.41 0 22.68 0z"
                            />
                        </svg>
                    </button>
                </div>
                {/* toogle btn for sign up or sign in  */}
                <button
                    type="button"
                    onClick={() => setIsSignUp(!isSignUp)}
                    className="toggle-auth"
                >
                    {isSignUp
                        ? "Already have an account? Sign in"
                        : "Don't have an account? Sign up"}
                </button>
            </div>
        </div>
    );
}

Auth.propTypes = {
    handle: PropTypes.func.isRequired,
    hideBtn: PropTypes.node.isRequired,
};
