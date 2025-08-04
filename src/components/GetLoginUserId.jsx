export const getUserId = () => {
    const authData = localStorage.getItem("sb-xwcuiteqnewdpfjykdei-auth-token");
  
    if (authData) {
      try {
        const parsedData = JSON.parse(authData);
        // setUserId(parsedData?.user?.id || null);
        return parsedData?.user?.id || null;
        // console.log("user id login ", userId);
        
      } catch (error) {
        console.error("Error parsing auth data:", error);
        return null;
      }
    }
    return null;
  };