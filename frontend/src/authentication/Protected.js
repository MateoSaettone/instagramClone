import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

function ProtectedPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const verifyToken = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');  // Redirect to login if token is missing
        return;
      }

      try {
        const response = await fetch('http://localhost:8000/verify-token/', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,  // Send token in Authorization header
          },
        });

        if (!response.ok) {
          throw new Error('Token verification failed');
        }

        setLoading(false); // Token is valid, allow access to the page
      } catch (error) {
        localStorage.removeItem('token');  // Remove invalid token
        navigate('/login');  // Redirect to login if token is invalid
      }
    };

    verifyToken();
  }, [navigate]);

  if (loading) {
    return <p>Loading...</p>;  // Show a loading message while token is being verified
  }

  return (
    <div>
      <h1>Protected Page</h1>
      <p>This is a protected page. Only visible to authenticated users.</p>
    </div>
  );
}

export default ProtectedPage;
