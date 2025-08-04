import { Navigate, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import PropTypes from "prop-types";
import { useAuth } from "./authUserContext";

export default function Protectedroutes({ children }) {
    const { loading, accessToken, refreshAccessToken } = useAuth(); //accessing the auth context js
    const [isRefreshing, setIsRefreshing] = useState(false);
    const location = useLocation(); // Access current location

    // console.log("location:", location);


    useEffect(() => {
        const attemptRefresh = async () => {
            if (!accessToken && !isRefreshing) {
                setIsRefreshing(true);
                await refreshAccessToken();
                setIsRefreshing(false);
            }
        };

        attemptRefresh();
    }, [accessToken, refreshAccessToken, isRefreshing]);

    // Show loading state while initial auth check or token refresh is in progress
    if (loading || isRefreshing) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>
        );
    }




    // If we have a valid access token, render the protected content
    if (accessToken) {
        return children;
    }

    // If no access token and not loading/refreshing, redirect to login
    return <Navigate to="/login" replace state={{ from: location }  } />;
}

Protectedroutes.propTypes = {
    children: PropTypes.node.isRequired,
};
