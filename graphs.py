import json
graphs = {}

#---------------------------------------------------------------------

graphs['bin_relay_log'] = {
    'config': {
	'global_attrs': {
	    'title': 'Binary/Relay Logs',
	    'vlabel': 'Log activity',
	},
	'data_source_attrs': {
	    'draw': 'LINE1',
	},
    },
    'data_sources': [
	{'name': 'Binlog_cache_disk_use', 'label': 'Binlog Cache Disk Use'},
	{'name': 'Binlog_cache_use',      'label': 'Binlog Cache Use'},
	{'name': 'ma_binlog_size',        'label': 'Binary Log Space'},
	{'name': 'relay_log_space',       'label': 'Relay Log Space'},
    ],
}

#---------------------------------------------------------------------

graphs['commands'] = {
    'config': {
	'global_attrs': {
	    'title': 'Command Counters',
	    'vlabel': 'Commands per ${graph_period}',
	    'total': 'Questions',
	},
	'data_source_attrs': {},
    },
    'data_sources': [
	{'name': 'Com_delete',         'label': 'Delete'},
	{'name': 'Com_insert',         'label': 'Insert'},
	{'name': 'Com_insert_select',  'label': 'Insert select'},
	{'name': 'Com_load',           'label': 'Load Data'},
	{'name': 'Com_replace',        'label': 'Replace'},
	{'name': 'Com_replace_select', 'label': 'Replace select'},
	{'name': 'Com_select',         'label': 'Select'},
	{'name': 'Com_update',         'label': 'Update'},
	{'name': 'Com_update_multi',   'label': 'Update multi'},
    ],
}

#---------------------------------------------------------------------

graphs['connections'] = {
    'config': {
	'global_attrs': {
	    'title': 'Connections',
	    'vlabel': 'Connections per ${graph_period}',
	},
	'data_source_attrs': {
	    'draw': 'LINE1',
	},
    },
    'data_sources': [
	{'name': 'max_connections',      'label': 'Max connections',
					 'type': 'GAUGE',
					 'draw': 'AREA',
					 'colour': 'cdcfc4'},
	{'name': 'Max_used_connections', 'label': 'Max used',
					 'type': 'GAUGE',
					 'draw': 'AREA',
					 'colour': 'ffd660'},
	{'name': 'Aborted_clients',      'label': 'Aborted clients'},
	{'name': 'Aborted_connects',     'label': 'Aborted connects'},
	{'name': 'Threads_connected',    'label': 'Threads connected',
					 'type': 'GAUGE'},
	{'name': 'Connections',          'label': 'New connections'},
    ],
}

#---------------------------------------------------------------------

graphs['files_tables'] = {
    'config': {
	'global_attrs': {
	    'title': 'Files and tables',
	    'vlabel': 'Tables',
	},
	'data_source_attrs': {
	    'type': 'GAUGE',
	    'draw': 'LINE1',
	},
    },
    'data_sources': [
	{'name': 'table_open_cache', 'label': 'Table cache',
				     'draw': 'AREA',
				     'colour': 'cdcfc4'},
	{'name': 'Open_files',       'label': 'Open files'},
	{'name': 'Open_tables',      'label': 'Open tables'},
	{'name': 'Opened_tables',    'label': 'Opened tables',
				     'type': 'GAUGE'},
    ],
}

#---------------------------------------------------------------------

graphs['innodb_bpool'] = {
    'config': {
	'global_attrs': {
	    'title': 'InnoDB Buffer Pool',
	    'vlabel': 'Pages',
	    'args': '--base 1024',
	},
	'data_source_attrs': {
	    'draw': 'LINE2',
	    'type': 'GAUGE',
	},
    },
    'data_sources': [
	{'name': 'ib_bpool_size',     'label': 'Buffer pool size',
				      'draw': 'AREA',
				      'colour': 'ffd660'},
	{'name': 'ib_bpool_dbpages',  'label': 'Database pages',
				      'draw': 'AREA',
				      'colour': 'cdcfc4'},
	{'name': 'ib_bpool_free',     'label': 'Free pages'},
	{'name': 'ib_bpool_modpages', 'label': 'Modified pages'},
    ],
}

#---------------------------------------------------------------------

graphs['innodb_bpool_act'] = {
    'config': {
	'global_attrs': {
	    'title': 'InnoDB Buffer Pool Activity',
	    'vlabel': 'Activity per ${graph_period}',
	    'total': 'Total',
	},
	'data_source_attrs': {
	    'draw': 'LINE2',
	},
    },
    'data_sources': [
	{'name': 'ib_bpool_read',    'label': 'Pages read'},
	{'name': 'ib_bpool_created', 'label': 'Pages created'},
	{'name': 'ib_bpool_written', 'label': 'Pages written'},
    ],
}

#---------------------------------------------------------------------

graphs['innodb_insert_buf'] = {
    'config': {
	'global_attrs': {
	    'title': 'InnoDB Insert Buffer',
	    'vlabel': 'Activity per ${graph_period}',
	},
	'data_source_attrs': {
	    'draw': 'LINE1',
	},
    },
    'data_sources': [
	{'name': 'ib_ibuf_inserts',    'label': 'Inserts'},
	{'name': 'ib_ibuf_merged_rec', 'label': 'Merged Records'},
	{'name': 'ib_ibuf_merges',     'label': 'Merges'},
    ],
}

#---------------------------------------------------------------------

graphs['innodb_io'] = {
    'config': {
	'global_attrs': {
	    'title': 'InnoDB IO',
	    'vlabel': 'IO operations per ${graph_period}',
	},
	'data_source_attrs': {
	    'draw': 'LINE1',
	},
    },
    'data_sources': [
	{'name': 'ib_io_read',  'label': 'File reads'},
	{'name': 'ib_io_write', 'label': 'File writes'},
	{'name': 'ib_io_log',   'label': 'Log writes'},
	{'name': 'ib_io_fsync', 'label': 'File syncs'},
    ],
}

#---------------------------------------------------------------------

graphs['innodb_io_pend'] = {
    'config': {
	'global_attrs': {
	    'title': 'InnoDB IO Pending',
	    'vlabel': 'Pending operations',
	},
	'data_source_attrs': {
	    'draw': 'LINE1',
	},
    },
    'data_sources': [
	{'name': 'ib_iop_log',         'label': 'AIO Log'},
	{'name': 'ib_iop_sync',        'label': 'AIO Sync'},
	{'name': 'ib_iop_flush_bpool', 'label': 'Buf Pool Flush'},
	{'name': 'ib_iop_flush_log',   'label': 'Log Flushes'},
	{'name': 'ib_iop_ibuf_aio',    'label': 'Insert Buf AIO Read'},
	{'name': 'ib_iop_aioread',     'label': 'Normal AIO Reads'},
	{'name': 'ib_iop_aiowrite',    'label': 'Normal AIO Writes'},
    ],
}

#---------------------------------------------------------------------

graphs['innodb_log'] = {
    'config': {
	'global_attrs': {
	    'title': 'InnoDB Log',
	    'vlabel': 'Log activity per ${graph_period}',
	},
	'data_source_attrs': {
	    'draw': 'LINE1',
	},
    },
    'data_sources': [
	{'name': 'innodb_log_buffer_size', 'label': 'Buffer Size',
					   'type': 'GAUGE',
					   'draw': 'AREA',
					   'colour': 'fafd9e'},
	{'name': 'ib_log_flush',           'label': 'KB Flushed'},
	{'name': 'ib_log_written',         'label': 'KB Written'},
    ],
}

#---------------------------------------------------------------------

graphs['innodb_rows'] = {
    'config': {
	'global_attrs': {
	    'title': 'InnoDB Row Operations',
	    'vlabel': 'Operations per ${graph_period}',
	    'total': 'Total',
	},
	'data_source_attrs': {},
    },
    'data_sources': [
	{'name': 'Innodb_rows_deleted',  'label': 'Deletes'},
	{'name': 'Innodb_rows_inserted', 'label': 'Inserts'},
	{'name': 'Innodb_rows_read',     'label': 'Reads'},
	{'name': 'Innodb_rows_updated',  'label': 'Updates'},
    ],
}

#---------------------------------------------------------------------

graphs['innodb_semaphores'] = {
    'config': {
	'global_attrs': {
	    'title': 'InnoDB Semaphores',
	    'vlabel': 'Semaphores per ${graph_period}',
	},
	'data_source_attrs': {
	    'draw': 'LINE1',
	},
    },
    'data_sources': [
	{'name': 'ib_spin_rounds', 'label': 'Spin Rounds'},
	{'name': 'ib_spin_waits',  'label': 'Spin Waits'},
	{'name': 'ib_os_waits',    'label': 'OS Waits'},
    ],
}

#---------------------------------------------------------------------

graphs['innodb_tnx'] = {
    'config': {
	'global_attrs': {
	    'title': 'InnoDB Transactions',
	    'vlabel': 'Transactions per ${graph_period}',
	},
	'data_source_attrs': {
	    'draw': 'LINE1',
	},
    },
    'data_sources': [
	{'name': 'ib_tnx', 'label': 'Transactions created'},
    ],
}

#---------------------------------------------------------------------

graphs['myisam_indexes'] = {
    'config': {
	'global_attrs': {
	    'title': 'MyISAM Indexes',
	    'vlabel': 'Requests per ${graph_period}',
	},
	'data_source_attrs': {
	    'draw': 'LINE2',
	},
    },
    'data_sources': [
	{'name': 'Key_read_requests',  'label': 'Key read requests'},
	{'name': 'Key_reads',          'label': 'Key reads'},
	{'name': 'Key_write_requests', 'label': 'Key write requests'},
	{'name': 'Key_writes',         'label': 'Key writes'},
   ],
}

#---------------------------------------------------------------------

graphs['network_traffic'] = {
    'config': {
	'global_attrs': {
	    'title': 'Network Traffic',
	    'args': '--base 1024',
	    'vlabel': 'Bytes received (-) / sent (+) per ${graph_period}',
	},
	'data_source_attrs': {
	    'draw': 'LINE2',
	},
    },
    'data_sources': [
	{'name': 'Bytes_received', 'label': 'Bytes transfered',
				   'graph': 'no'},
	{'name': 'Bytes_sent',     'label': 'Bytes transfered',
				   'negative': 'Bytes_received'},
    ],
}

#---------------------------------------------------------------------

graphs['qcache'] = {
    'config': {
	'global_attrs': {
	    'title': 'Query Cache',
	    'vlabel': 'Commands per ${graph_period}',
	},
	'data_source_attrs': {
	     'draw': 'LINE1',
	},
    },
    'data_sources': [
	{'name': 'Qcache_queries_in_cache', 'label': 'Queries in cache'},
	{'name': 'Qcache_hits',             'label': 'Cache hits'},
	{'name': 'Qcache_inserts',          'label': 'Inserts'},
	{'name': 'Qcache_not_cached',       'label': 'Not cached'},
	{'name': 'Qcache_lowmem_prunes',    'label': 'Low-memory prunes'},
    ],
}

#---------------------------------------------------------------------

graphs['qcache_mem'] = {
    'config': {
	'global_attrs': {
	    'title': 'Query Cache Memory',
	    'vlabel': 'Bytes',
	    'args': '--base 1024 --lower-limit 0',
	},
	'data_source_attrs': {
	    'draw': 'AREA',
	    'type': 'GAUGE',
	},
    },
    'data_sources': [
	{'name': 'query_cache_size',    'label': 'Cache size'},
	{'name': 'Qcache_free_memory',  'label': 'Free mem'},
    ],
}


#---------------------------------------------------------------------

graphs['select_types'] = {
    'config': {
	'global_attrs': {
	    'title': 'Select types',
	    'vlabel': 'Commands per ${graph_period}',
	    'total': 'Total',
	},
	'data_source_attrs': {},
    },
    'data_sources': [
	{'name': 'Select_full_join',       'label': 'Full join'},
	{'name': 'Select_full_range_join', 'label': 'Full range'},
	{'name': 'Select_range',           'label': 'Range'},
	{'name': 'Select_range_check',     'label': 'Range check'},
	{'name': 'Select_scan',            'label': 'Scan'},
    ],
}

#---------------------------------------------------------------------

graphs['slow'] = {
    'config': {
	'global_attrs': {
	    'title': 'Slow Queries',
	    'vlabel': 'Slow queries per ${graph_period}',
	},
	'data_source_attrs': {
	    'draw': 'LINE2',
	},
    },
    'data_sources': [
	{'name': 'Slow_queries', 'label': 'Slow queries'},
    ],
}

#---------------------------------------------------------------------

graphs['sorts'] = {
    'config': {
	'global_attrs': {
	    'title': 'Sorts',
	    'vlabel': 'Sorts / ${graph_period}',
	},
	'data_source_attrs': {
	    'draw': 'LINE2',
	},
    },
    'data_sources': [
	{'name': 'Sort_rows',         'label': 'Rows sorted'},
	{'name': 'Sort_range',        'label': 'Range'},
	{'name': 'Sort_merge_passes', 'label': 'Merge passes'},
	{'name': 'Sort_scan',         'label': 'Scan'},
    ],
}

#---------------------------------------------------------------------

graphs['table_locks'] = {
    'config': {
	'global_attrs': {
	    'title': 'Table locks',
	    'vlabel': 'locks per ${graph_period}',
	},
	'data_source_attrs': {
	    'draw': 'LINE2',
	},
    },
    'data_sources': [
	{'name': 'Table_locks_immediate', 'label': 'Table locks immed'},
	{'name': 'Table_locks_waited',    'label': 'Table locks waited'},
    ],
}

#---------------------------------------------------------------------

graphs['tmp_tables'] = {
    'config': {
	'global_attrs': {
	    'title': 'Temporary objects',
	    'vlabel': 'Objects per ${graph_period}',
	},
	'data_source_attrs': {
	    'draw': 'LINE2',
	},
    },
    'data_sources': [
	{'name': 'Created_tmp_disk_tables', 'label': 'Temp disk tables'},
	{'name': 'Created_tmp_tables',      'label': 'Temp tables'},
	{'name': 'Created_tmp_files',       'label': 'Temp files'},
    ],
}

print json.dumps(graphs)
