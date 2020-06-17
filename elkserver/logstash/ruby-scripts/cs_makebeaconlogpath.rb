#
# Part of RedELK
# Script to have logstash insert an extra field pointing to the full TXT file of a Cobalt Strike keystrokes file
#
# Author: Outflank B.V. / Marc Smeets
#

def register(params)
#        @timestamp = params["timestamp"]
#        @source = param["source"]
#	@implant_id = param["implant_id"]
end

def filter(event)
	host = event.get("[beat][name]")
	logpath = event.get("source")
	implant_id = event.get("implant_id")
	temppath = logpath.split('/cobaltstrike')
	temppath2 = temppath[1].split(/\/([^\/]*)$/)
	implantlogpath = "/c2logs/" + "#{host}" + "#{temppath[1]}"
	event.tag("_rubyparseok")
    event.set("implantlogfile", implantlogpath)
	return [event]
end
