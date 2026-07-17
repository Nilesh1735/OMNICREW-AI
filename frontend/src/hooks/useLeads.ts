import { useState, useEffect } from 'react';
import { LeadData } from '../types';

// Dynamic API URL for deployment
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_URL = `${API_BASE_URL}/api/leads`;

export const useLeads = () => {
  const [leads, setLeads] = useState<LeadData[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchLeads = async () => {
      try {
        const response = await fetch(API_URL, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('omnicrew_token') || 'no_token'}`
          }
        });
        if (!response.ok) throw new Error('Failed to fetch leads');
        const data = await response.json();
        setLeads(data);
      } catch (error) {
        console.error(error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchLeads();
    const interval = setInterval(fetchLeads, 10000);

    return () => clearInterval(interval);
  }, []);

  return { leads, isLoading };
};