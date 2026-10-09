import { Typography, Box, Button, Alert } from '@mui/material';
import apiClient from '../../api/client.js';
import {useState} from 'react'

function HealthPage( { setNotification } ) {
    const [healthData, setHealthData] = useState(null);
    const [errorMsg, setErrorMsg] = useState(null);

  const checkHealth = async () => {
    setHealthData(null);
    setErrorMsg(null);
  try {
      const response = await apiClient.get('/health/detail');
      setHealthData(response.data);

    } catch (err) {
      const msg = 
        err.response?.data?.detail || 
        (err.response?.status === 403 ? 'Access denied: ADMIN role required.' : null) ||
        err.message || 
        'Health check failed.';
        
      setErrorMsg(msg);
      setHealthData({ db_status: 'unknown', s3_status: 'unknown' });
    }
  };



  return (
    <>
        <Typography variant="h5"  gutterBottom>
          Health
        </Typography>
        <Box sx={{ mb: 4}}>
            <Button variant="outlined" sx={{ mb: 2}} onClick={checkHealth} >Check App Health</Button>
        
        

            {healthData && (
          <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Alert severity={healthData.db_status === 'ok' ? 'Ok' : 'Failed'}>
              Database Status: {healthData.db_status.toUpperCase()}
            </Alert>
            <Alert severity={healthData.s3_status === 'ok' ? 'Ok' : 'Failed'}>
              S3 Status: {healthData.s3_status.toUpperCase()}
            </Alert>
          </Box>
        )}
        </Box>

        {errorMsg && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {errorMsg}
          </Alert>
        )}
    </>
  );
}

export default HealthPage;