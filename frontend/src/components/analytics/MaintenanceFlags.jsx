import { useEffect, useState } from 'react';
import {
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import apiClient from '../../api/client.js';

function MaintenanceFlags() {
  const [flags, setFlags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchFlags() {
      try {
        const response = await apiClient.get('/farms/maintenance-flags');
        setFlags(response.data);
      } catch {
        setError('Could not load maintenance flags.');
      } finally {
        setLoading(false);
      }
    }
    fetchFlags();
  }, []);

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;
  if (flags.length === 0) {
    return <Typography>No farms currently over the 30% maintenance threshold.</Typography>;
  }

  return (
    <TableContainer>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Farm</TableCell>
            <TableCell align="right">Total Equipment</TableCell>
            <TableCell align="right">In Maintenance</TableCell>
            <TableCell align="right">Percentage</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {flags.map((row) => (
            <TableRow key={row.farm_id}>
              <TableCell>{row.farm_name}</TableCell>
              <TableCell align="right">{row.total_equipments}</TableCell>
              <TableCell align="right">{row.maintenance_count}</TableCell>
              <TableCell align="right">{row.maintenance_percentage}%</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

export default MaintenanceFlags;