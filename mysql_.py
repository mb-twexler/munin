#!/usr/bin/env python
# encoding: utf-8
# Munin magic markers 
#%# family=auto
#%# capabilities=autoconf suggest
"""
mysql_.py

Created by Ted Wexler on 2011-05-20.
Copyright (c) 2011 Malwarebytes Corp. All rights reserved.
"""
from __future__ import with_statement
import os,sys,re,stat
#for testing


class munin_mysql:
	results = {}
	graphs = None
	mysqluser, mysqlpass, mysqlhost = "", "", ""
	defaults = {
	    'global_attrs': {
	        'args': '--base 1000',
	    },
	    'data_source_attrs': {
	        'min':  '0',
	        'type': 'DERIVE',
	        'draw': 'AREASTACK',
	    },
	}
	def __init__(self):
		pass
	def main(self,argv):
#		for testing purposes
#		with open("statusout.txt") as f:
#			innodbStatusText = ''.join(f.readlines()[:-3])
		mygraphs = MuninMysqlGraphs()
		self.graphs = mygraphs.graphs
		try: self.mysqluser, self.mysqlpass, self.mysqlhost = os.environ['mysqluser'], os.environ['mysqlpass'], os.environ['mysqlhost']
		except KeyError:
			print "please configure this plugin in /etc/munin/plugin-conf.d/"
			sys.exit(255)
		if len(argv) > 1:
			command = argv[1]
			if command == 'config': pass
			else:
				try: eval('self.'+command+'()')
				except NameError:
					print "no such command "+command
					sys.exit(255)
		if len(argv[0].split("mysql_")) > 0:
			graph = argv[0].split("mysql_")[1]
			if len(argv) > 1:
				 if argv[1] == 'config': self.config(graph)
			conn,cur = self.db_connect()
			cur.execute("SHOW ENGINE INNODB STATUS;")
			r = cur.fetchone()
			innodbStatusText = r[2] # element 2 always has the data
			cur.execute('SELECT VERSION();')
			mysql_version = cur.fetchone()[0] # element 0 always has the data
			self.update_variables(cur)
			cur.close()
			conn.close()
			innodbParser = InnoDBStatusParser(innodbStatusText, mysql_version)
			self.results.update(innodbParser.results)
			self.show(graph)
	def db_connect(self):
		try:
			import MySQLdb
		except ImportError:
			print "you need to install the MySQLdb module before using this plugin"
			sys.exit(0)
		try:
			conn = MySQLdb.connect(self.mysqlhost, self.mysqluser, self.mysqlpass)
		except OperationalError:
			print "failed connecting to the database, check your config"
		cur = conn.cursor()
		return (conn,cur)
	def autoconf(self):
		self.db_connect()
		print "yes"
		sys.exit(0)
	def suggest(self):
		for graph in self.graphs:
			print graph
		sys.exit(0)
	def config(self, graph_name):
		if graph_name not in self.graphs: 
			print "unknown graph "+graph_name
			sys.exit(2)
		graph = self.graphs[graph_name]
		conf = self.defaults['global_attrs'] 
		conf.update(graph['config']['global_attrs'])
		for k,v in conf.items():
			print "graph_%s %s" % (k,v)
		data_source_attrs = self.defaults['data_source_attrs']
		data_source_attrs.update(graph['config']['data_source_attrs'])
		print "graph_category mysql2"
		for ds in graph['data_sources']:
			for k,v in data_source_attrs.items():
				print "%s.%s %s" % (ds['name'],k,v)
			for k1,v1 in ds.items():
				if 'name' in k1: continue
				print "%s.%s %s" % (ds['name'],k1,v1) 
		sys.exit(0)
	def show(self, graph_name):
		if graph_name not in self.graphs: 
			print "unknown graph "+graph_name
			sys.exit(2)
		graph = self.graphs[graph_name]
		for ds in graph['data_sources']:
			print "%s.value %s" % (ds['name'], self.results[ds['name']])
	def update_variables(self, cursor):
		queries = [ 'SHOW GLOBAL VARIABLES;', 'SHOW GLOBAL STATUS;' ]
		for query in queries:
			cursor.execute(query)
			r = cursor.fetchall()
			for k ,v in r:
				self.results[k] = v
class InnoDBStatusParser:
	results = {}
	data = {}
	mysql_version = None
	def __init__(self, statusText, mysql_version):
		self.mysql_version = mysql_version
		self.data = self.parse_innodb_status(statusText)
		self.parse_semaphores()
		self.parse_bpool_and_memory()
		self.parse_transactions()
		self.parse_file_io()
		self.parse_ibuffer_hash_index()
		self.parse_log()
#		print self.results

	def parse_innodb_status(self, statusString):
		datadict = {}
		headRegex = "-+\n([A-Z /]*)\n-+"
		keys = re.compile(headRegex).findall(statusString)
		values = re.sub(headRegex, "\n\n\n", statusString).split("\n\n\n\n")[1:] #first element in that array is always null string
		i=0
		for key in keys:
			datadict[key] = values[i].lstrip().rstrip() #always seem to get some extra whitespace on both sides
			i += 1
		return datadict
		
	def parse_semaphores(self):
		semaphores = self.data['SEMAPHORES']
		regex = "Mutex spin waits (\d+), rounds (\d+), OS waits (\d+)\n"
		res = re.compile(regex).findall(semaphores)[0]
		self.results['ib_spin_waits'], self.results['ib_spin_rounds'], self.results['ib_os_waits'] = res
	def parse_bpool_and_memory(self):
		bpoolmemory = self.data["BUFFER POOL AND MEMORY"]
		self.results['ib_bpool_size'] = re.compile('Buffer pool size\s+(\d+)\n').findall(bpoolmemory)[0]
		self.results['ib_bpool_free'] = re.compile('Free buffers\s+(\d+)\n').findall(bpoolmemory)[0]
		self.results['ib_bpool_dbpages'] = re.compile('Database pages\s+(\d+)\n').findall(bpoolmemory)[0]
		self.results['ib_bpool_modpages'] = re.compile('Modified db pages\s+(\d+)\n').findall(bpoolmemory)[0]
		res = re.compile('Pages read (\d+), created (\d+), written (\d+)\n').findall(bpoolmemory)[0]
		self.results['ib_bpool_read'], self.results['ib_bpool_created'], self.results['ib_bpool_written'] = res
	def parse_transactions(self):
		transactions = self.data['TRANSACTIONS']
		#we have to have some logic to sort out mysql version 5.1 and 5.5 because they don't use bigint anymore
		if '5.5' in self.mysql_version:
			ib_tnx = re.compile('Trx id counter ([0-9A-Z]+)\n').findall(transactions)[0]
			self.results['ib_tnx'] = self.parse_bigint(ib_tnx)
			self.results['ib_tnx_prg'] = re.compile('Purge done for trx\'s n:o < (\d+).*').findall(transactions)[0]
		else:
			ib_tnx = re.compile('Trx id counter 0 ([0-9A-Z]+)\n').findall(transactions)[0]					
			self.results['ib_tnx'] = self.parse_bigint(ib_tnx)
			self.results['ib_tnx_prg'] = re.compile('Purge done for trx\'s n:o < 0 (\d+).*').findall(transactions)[0]	
		self.results['ib_tnx_hist'] = re.compile('History list length (\d+)\n').findall(transactions)[0]
		
	def parse_file_io(self):
		fileio = self.data['FILE I/O']
		res = {}
		#we have to have some logic to sort out mysql version 5.1 and 5.5 because the output is slightly different
		if '5.5' in self.mysql_version:
			re1 = 'Pending normal aio reads: (\d+).*, aio writes: (\d+).*,\n\s*ibuf aio reads: (\d+), log i\/o\'s: (\d+), sync i\/o\'s: (\d+)\n'
		else:	
			re1 = 'Pending normal aio reads: (\d+), aio writes: (\d+),\n\s*ibuf aio reads: (\d+), log i\/o\'s: (\d+), sync i\/o\'s: (\d+)\n'
		re2 = 'Pending flushes \(fsync\) log: (\d+); buffer pool: (\d+)\n'
		re3 = '(\d+) OS file reads, (\d+) OS file writes, (\d+) OS fsyncs\n'
		res1 = re.compile(re1).findall(fileio, re.DOTALL)[0] 
		res2 = re.compile(re2).findall(fileio)[0]
		res3 = re.compile(re3).findall(fileio)[0]
		res['ib_iop_aioread'],res['ib_iop_aiowrite'],res['ib_iop_ibuf_aio'],res['ib_iop_log'],res['ib_iop_sync'] = res1
		res['ib_iop_flush_log'],res['ib_iop_flush_bpool'] = res2
		res['ib_io_read'],res['ib_io_write'],res['ib_io_fsync'] = res3
		self.results.update(res)
	def parse_ibuffer_hash_index(self):
		data = self.data['INSERT BUFFER AND ADAPTIVE HASH INDEX']
		# we have to have some logic to sort out mysql version 5.1 and 5.5 because the output is slightly different,
		# and 5.5's INNODB STATUS doesn't seem to have merged recs count, so we set that to 0 for compatibility
		if '5.5' in self.mysql_version:
			res = re.compile('Ibuf: size \d+, free list len \d+, seg size \d+, (\d+) merges\nmerged operations:\n insert (\d+), delete mark \d+, delete \d+').findall(data)[0]
			self.results['ib_ibuf_merged_rec'] = 0
			self.results['ib_ibuf_merges'],self.results['ib_ibuf_inserts'] = res
		else:
			res = re.compile('(\d+) inserts, (\d+) merged recs, (\d+) merges\n').findall(data)[0]
			self.results['ib_ibuf_inserts'],self.results['ib_ibuf_merged_rec'],self.results['ib_ibuf_merges'] = res
	def parse_log(self):
		log = self.data['LOG']
		res = re.compile('Log sequence.*(\d+)\nLog flushed.* (\d+)', re.DOTALL).findall(log)[0]
		res2 = re.compile("(\d+) log i\/o.*done")
		self.results['ib_log_written'],self.results['ib_log_flush'] = res
		self.results['ib_io_log'] = res2[0]
	def parse_bigint(self, i):
		try: ret = str(int(i))
		except ValueError: ret = str(int(eval("0x"+i)))
		if not ret: ret = 0
		return ret

class MuninMysqlGraphs:
	graphs = {"innodb_insert_buf": {"config": {"data_source_attrs": {"draw": "LINE1"}, "global_attrs": {"vlabel": "Activity per ${graph_period}", "title": "InnoDB Insert Buffer"}}, "data_sources": [{"name": "ib_ibuf_inserts", "label": "Inserts"}, {"name": "ib_ibuf_merged_rec", "label": "Merged Records"}, {"name": "ib_ibuf_merges", "label": "Merges"}]}, "qcache": {"config": {"data_source_attrs": {"draw": "LINE1"}, "global_attrs": {"vlabel": "Commands per ${graph_period}", "title": "Query Cache"}}, "data_sources": [{"name": "Qcache_queries_in_cache", "label": "Queries in cache"}, {"name": "Qcache_hits", "label": "Cache hits"}, {"name": "Qcache_inserts", "label": "Inserts"}, {"name": "Qcache_not_cached", "label": "Not cached"}, {"name": "Qcache_lowmem_prunes", "label": "Low-memory prunes"}]}, "innodb_io_pend": {"config": {"data_source_attrs": {"draw": "LINE1"}, "global_attrs": {"vlabel": "Pending operations", "title": "InnoDB IO Pending"}}, "data_sources": [{"name": "ib_iop_log", "label": "AIO Log"}, {"name": "ib_iop_sync", "label": "AIO Sync"}, {"name": "ib_iop_flush_bpool", "label": "Buf Pool Flush"}, {"name": "ib_iop_flush_log", "label": "Log Flushes"}, {"name": "ib_iop_ibuf_aio", "label": "Insert Buf AIO Read"}, {"name": "ib_iop_aioread", "label": "Normal AIO Reads"}, {"name": "ib_iop_aiowrite", "label": "Normal AIO Writes"}]}, "connections": {"config": {"data_source_attrs": {"draw": "LINE1"}, "global_attrs": {"vlabel": "Connections per ${graph_period}", "title": "Connections"}}, "data_sources": [{"colour": "cdcfc4", "draw": "AREA", "type": "GAUGE", "name": "max_connections", "label": "Max connections"}, {"colour": "ffd660", "draw": "AREA", "type": "GAUGE", "name": "Max_used_connections", "label": "Max used"}, {"name": "Aborted_clients", "label": "Aborted clients"}, {"name": "Aborted_connects", "label": "Aborted connects"}, {"type": "GAUGE", "name": "Threads_connected", "label": "Threads connected"}, {"name": "Connections", "label": "New connections"}]}, "select_types": {"config": {"data_source_attrs": {}, "global_attrs": {"total": "Total", "vlabel": "Commands per ${graph_period}", "title": "Select types"}}, "data_sources": [{"name": "Select_full_join", "label": "Full join"}, {"name": "Select_full_range_join", "label": "Full range"}, {"name": "Select_range", "label": "Range"}, {"name": "Select_range_check", "label": "Range check"}, {"name": "Select_scan", "label": "Scan"}]}, "network_traffic": {"config": {"data_source_attrs": {"draw": "LINE2"}, "global_attrs": {"args": "--base 1024", "vlabel": "Bytes received (-) / sent (+) per ${graph_period}", "title": "Network Traffic"}}, "data_sources": [{"graph": "no", "name": "Bytes_received", "label": "Bytes transfered"}, {"negative": "Bytes_received", "name": "Bytes_sent", "label": "Bytes transfered"}]}, "innodb_semaphores": {"config": {"data_source_attrs": {"draw": "LINE1"}, "global_attrs": {"vlabel": "Semaphores per ${graph_period}", "title": "InnoDB Semaphores"}}, "data_sources": [{"name": "ib_spin_rounds", "label": "Spin Rounds"}, {"name": "ib_spin_waits", "label": "Spin Waits"}, {"name": "ib_os_waits", "label": "OS Waits"}]}, "myisam_indexes": {"config": {"data_source_attrs": {"draw": "LINE2"}, "global_attrs": {"vlabel": "Requests per ${graph_period}", "title": "MyISAM Indexes"}}, "data_sources": [{"name": "Key_read_requests", "label": "Key read requests"}, {"name": "Key_reads", "label": "Key reads"}, {"name": "Key_write_requests", "label": "Key write requests"}, {"name": "Key_writes", "label": "Key writes"}]}, "slow": {"config": {"data_source_attrs": {"draw": "LINE2"}, "global_attrs": {"vlabel": "Slow queries per ${graph_period}", "title": "Slow Queries"}}, "data_sources": [{"name": "Slow_queries", "label": "Slow queries"}]}, "innodb_bpool_act": {"config": {"data_source_attrs": {"draw": "LINE2"}, "global_attrs": {"total": "Total", "vlabel": "Activity per ${graph_period}", "title": "InnoDB Buffer Pool Activity"}}, "data_sources": [{"name": "ib_bpool_read", "label": "Pages read"}, {"name": "ib_bpool_created", "label": "Pages created"}, {"name": "ib_bpool_written", "label": "Pages written"}]}, "sorts": {"config": {"data_source_attrs": {"draw": "LINE2"}, "global_attrs": {"vlabel": "Sorts / ${graph_period}", "title": "Sorts"}}, "data_sources": [{"name": "Sort_rows", "label": "Rows sorted"}, {"name": "Sort_range", "label": "Range"}, {"name": "Sort_merge_passes", "label": "Merge passes"}, {"name": "Sort_scan", "label": "Scan"}]}, "innodb_bpool": {"config": {"data_source_attrs": {"draw": "LINE2", "type": "GAUGE"}, "global_attrs": {"args": "--base 1024", "vlabel": "Pages", "title": "InnoDB Buffer Pool"}}, "data_sources": [{"colour": "ffd660", "draw": "AREA", "name": "ib_bpool_size", "label": "Buffer pool size"}, {"colour": "cdcfc4", "draw": "AREA", "name": "ib_bpool_dbpages", "label": "Database pages"}, {"name": "ib_bpool_free", "label": "Free pages"}, {"name": "ib_bpool_modpages", "label": "Modified pages"}]}, "tmp_tables": {"config": {"data_source_attrs": {"draw": "LINE2"}, "global_attrs": {"vlabel": "Objects per ${graph_period}", "title": "Temporary objects"}}, "data_sources": [{"name": "Created_tmp_disk_tables", "label": "Temp disk tables"}, {"name": "Created_tmp_tables", "label": "Temp tables"}, {"name": "Created_tmp_files", "label": "Temp files"}]}, "qcache_mem": {"config": {"data_source_attrs": {"draw": "AREA", "type": "GAUGE"}, "global_attrs": {"args": "--base 1024 --lower-limit 0", "vlabel": "Bytes", "title": "Query Cache Memory"}}, "data_sources": [{"name": "query_cache_size", "label": "Cache size"}, {"name": "Qcache_free_memory", "label": "Free mem"}]}, "innodb_tnx": {"config": {"data_source_attrs": {"draw": "LINE1"}, "global_attrs": {"vlabel": "Transactions per ${graph_period}", "title": "InnoDB Transactions"}}, "data_sources": [{"name": "ib_tnx", "label": "Transactions created"}]}, "innodb_rows": {"config": {"data_source_attrs": {}, "global_attrs": {"total": "Total", "vlabel": "Operations per ${graph_period}", "title": "InnoDB Row Operations"}}, "data_sources": [{"name": "Innodb_rows_deleted", "label": "Deletes"}, {"name": "Innodb_rows_inserted", "label": "Inserts"}, {"name": "Innodb_rows_read", "label": "Reads"}, {"name": "Innodb_rows_updated", "label": "Updates"}]}, "commands": {"config": {"data_source_attrs": {}, "global_attrs": {"total": "Questions", "vlabel": "Commands per ${graph_period}", "title": "Command Counters"}}, "data_sources": [{"name": "Com_delete", "label": "Delete"}, {"name": "Com_insert", "label": "Insert"}, {"name": "Com_insert_select", "label": "Insert select"}, {"name": "Com_load", "label": "Load Data"}, {"name": "Com_replace", "label": "Replace"}, {"name": "Com_replace_select", "label": "Replace select"}, {"name": "Com_select", "label": "Select"}, {"name": "Com_update", "label": "Update"}, {"name": "Com_update_multi", "label": "Update multi"}]}, "bin_relay_log": {"config": {"data_source_attrs": {"draw": "LINE1"}, "global_attrs": {"vlabel": "Log activity", "title": "Binary/Relay Logs"}}, "data_sources": [{"name": "Binlog_cache_disk_use", "label": "Binlog Cache Disk Use"}, {"name": "Binlog_cache_use", "label": "Binlog Cache Use"}, {"name": "ma_binlog_size", "label": "Binary Log Space"}, {"name": "relay_log_space", "label": "Relay Log Space"}]}, "innodb_io": {"config": {"data_source_attrs": {"draw": "LINE1"}, "global_attrs": {"vlabel": "IO operations per ${graph_period}", "title": "InnoDB IO"}}, "data_sources": [{"name": "ib_io_read", "label": "File reads"}, {"name": "ib_io_write", "label": "File writes"}, {"name": "ib_io_log", "label": "Log writes"}, {"name": "ib_io_fsync", "label": "File syncs"}]}, "innodb_log": {"config": {"data_source_attrs": {"draw": "LINE1"}, "global_attrs": {"vlabel": "Log activity per ${graph_period}", "title": "InnoDB Log"}}, "data_sources": [{"colour": "fafd9e", "draw": "AREA", "type": "GAUGE", "name": "innodb_log_buffer_size", "label": "Buffer Size"}, {"name": "ib_log_flush", "label": "KB Flushed"}, {"name": "ib_log_written", "label": "KB Written"}]}, "table_locks": {"config": {"data_source_attrs": {"draw": "LINE2"}, "global_attrs": {"vlabel": "locks per ${graph_period}", "title": "Table locks"}}, "data_sources": [{"name": "Table_locks_immediate", "label": "Table locks immed"}, {"name": "Table_locks_waited", "label": "Table locks waited"}]}, "files_tables": {"config": {"data_source_attrs": {"draw": "LINE1", "type": "GAUGE"}, "global_attrs": {"vlabel": "Tables", "title": "Files and tables"}}, "data_sources": [{"colour": "cdcfc4", "draw": "AREA", "name": "table_open_cache", "label": "Table cache"}, {"name": "Open_files", "label": "Open files"}, {"name": "Open_tables", "label": "Open tables"}, {"type": "GAUGE", "name": "Opened_tables", "label": "Opened tables"}]}}
	def __init__(self):
		pass

class MuninMysqlCache:
	file = "/tmp/munin-mysql.tmp"
	def __init__(self):
		st = os.stat(self.file).st_mode
		if stat.S_ISREG(st):
			
if __name__ == '__main__':
	m = munin_mysql()
	m.main(sys.argv)

