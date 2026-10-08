import { Typography, Box } from '@mui/material';
import FarmDataGrid from '../farms/FarmDataGrid.jsx'

function FarmsPage( { setNotification } ) {
  return (
    <>
        <Typography variant="h5" component="h2" gutterBottom>
          Farms
        </Typography>
        <Box sx={{ mb: 4}}>
          <FarmDataGrid onSuccess={setNotification}/>
        </Box>
    </>
  );
}

export default FarmsPage;