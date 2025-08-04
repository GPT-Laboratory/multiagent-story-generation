import { Outlet, useNavigate } from "react-router-dom";
import { Footer, Header } from "antd/es/layout/layout";
import { RQicon } from "../mysvg";
// for authentication
import { useState, useRef, useEffect } from "react";
import { useAuth } from "./authUserContext.jsx";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faUser, faSignOut } from "@fortawesome/free-solid-svg-icons";
import supabase from "./supabaseClient.jsx";
import { useLocation } from "react-router-dom";
import './Layout.css'

const Layout = () => {
	// all variables and hook for authentication
	const userElement = <FontAwesomeIcon icon={faUser} />;
	const Signout = <FontAwesomeIcon icon={faSignOut} />;
	const [showSignUp, setShowSignUp] = useState(false);
	const { user } = useAuth();
	const [showDropdown, setShowDropDown] = useState(false);
	const profileBtnRef = useRef();
	const dropdownRef = useRef();
	const imgElement = user?.user_metadata.picture ?? null;
	const location = useLocation();
	const pathName = location.pathname;
	const navigate = useNavigate();



	// handling logging out the user
	const handleLogout = async () => {
		try {
			const { error } = await supabase.auth.signOut();
			if (error) throw error;
			localStorage.clear();
			window.location.href = "/";
		} catch (error) {
			console.log("Error occured while signout: ", error);
			alert("Error while Signout. Try Again!");
		}
	};

	// // func to toggle authentication component
	// function handleButtonClick(val) {
	// 	setShowSignUp(val);
	// }


	// for toggling effect of dropdown
	useEffect(() => {
		const handleWindowClick = (event) => {
			if (
				(dropdownRef.current &&
					!dropdownRef.current.contains(event.target)) && // Click is outside dropdown
				(profileBtnRef.current &&
					!profileBtnRef.current.contains(event.target)) // Click is outside profile button
			) {
				setShowDropDown(false); // Close dropdown
			}
		};

		if (showDropdown) {
			window.addEventListener("click", handleWindowClick);
		}

		return () => {
			window.removeEventListener("click", handleWindowClick);
		};
	}, [showDropdown]);

	// taking buttom ref
	const authBtnRef = useRef(null);

	useEffect(() => {
		if (authBtnRef.current) {
			if (user) {
				authBtnRef.current.classList.remove("before-btn");
				authBtnRef.current.classList.add("btn");
			}
			else {
				authBtnRef.current.classList.remove("btn");
				authBtnRef.current.classList.add("before-btn");
			}
		}
	}, [user])

	//  for hiding signin/up button if the user redirect to /login
	// useEffect(() => {
	// 	console.log("pathname in layout", pathName);
	// 	console.log("auth button ref", authBtnRef.current)

	// 	if (authBtnRef.current) {
	// 		if (pathName == "/login") {
	// 			authBtnRef.current.style.display = "none";
	// 		}
	// 		else{
	// 			authBtnRef.current.style.display = "";
	// 		}
	// 	}
	// }, [pathName])

	return (
		<div>
			<Header style={{ backgroundColor: "#f3fff3", overflow: 'hidden' }}>
				<div
					style={{
						display: "flex",
						flexDirection: "row",
						justifyContent: "space-between",
						marginLeft: "0px",
						// border:'1px solid red',
						// width: "100%",
					}}>
					<div
						style={{
							// border:'1px solid blue',
						}}
					>
						<RQicon
							width={"60px"}
							height={"60px"}
						/>
					</div>
					<div style={{ fontSize: "20px", color: "black", marginLeft: '350px', }}>
						<strong>Multi-Agent Requirement Tool</strong>
					</div>
					{/* toogle the button and component by conditional rendering */}
					<div className="element" style={{
						// border:'1px solid blue',
					}}>

						{!showSignUp && !user && (
							<button
								ref={authBtnRef}
								className="btn before-btn"
								onClick={() => {
									navigate("/login");
								}}
							>
								Sign Up/Log in
							</button>
						)}
						{!showSignUp && user && (
							<div>
								{/* <button
									className="btn btnflex"
									ref={profileBtnRef}
									onClick={() => {
										setShowDropDown(!showDropdown);
									}}
								>
									{user.user_metadata?.avatar_url ? (
										<img
											src={imgElement}
											alt="profile"
											className="w-8 h-8 rounded-full object-cover profileimg"
										/>
									) : (
										{ userelement: userElement }
									)}
								</button> */}
								<button
									className="btn btnflex"
									ref={profileBtnRef}
									onClick={() => {
										setShowDropDown(!showDropdown);
									}}
								>
									{user.user_metadata?.avatar_url ? (
										<img
											src={imgElement}
											alt="profile"
											className="w-8 h-8 rounded-full object-cover profileimg"
										/>
									) : (
										userElement  // Just use the variable directly, not in an object
									)}
								</button>
								{showDropdown && (
									<div className="dropdown-content " ref={dropdownRef}>
										<div className="user-info">
											<p className="user-name">
												{user.user_metadata?.full_name || "User"}
											</p>
											<p className="user-email">{user.email}</p>
										</div>
										<div className="line"></div>

										<button onClick={handleLogout} className="logout-button">
											{Signout}
											Logout
										</button>
									</div>
								)}

							</div>
						)}
						{/* {showSignUp && <Auth handle={handleButtonClick} />} */}
					</div>
					<div></div>
				</div>
			</Header>
			<main>
				<Outlet /> {/* This renders the child components */}
			</main>
			<Footer className="footerFixed">
				<div style={{ float: "right", lineHeight: 0 }}>
					<p>&copy; {new Date().getFullYear()} GPT LAB. All rights reserved.</p>
				</div>
			</Footer>
		</div>
	);
};

export default Layout;
