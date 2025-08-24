# -*- coding: utf-8 -*-
# Dynamically generated protobuf module for EmbeddingEvent.
# This avoids requiring protoc at build time in constrained environments.

from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

_sym_db = _symbol_database.Default()

# Build a FileDescriptorProto for the schema defined in tools/embedding_intelligence/proto/gtm.proto
_file = _descriptor_pb2.FileDescriptorProto()
_file.name = 'tools/embedding_intelligence/proto/gtm.proto'
_file.package = 'embeddingintelligence'
_file.syntax = 'proto3'

# Define EmbeddingEvent message
_msg = _file.message_type.add()
_msg.name = 'EmbeddingEvent'

# Helper to add fields

def _add_field(msg, name, number, field_type, label=_descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL):
	f = msg.field.add()
	f.name = name
	f.number = number
	f.label = label
	f.type = field_type

# Fields (matching the .proto)
_add_field(_msg, 'event_id', 1, _descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_msg, 'timestamp_ms', 2, _descriptor_pb2.FieldDescriptorProto.TYPE_INT64)
_add_field(_msg, 'project_name', 3, _descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_msg, 'crash_signature', 4, _descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_msg, 'crash_type', 5, _descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_msg, 'embedding_used', 6, _descriptor_pb2.FieldDescriptorProto.TYPE_BOOL)
_add_field(_msg, 'cache_hit', 7, _descriptor_pb2.FieldDescriptorProto.TYPE_BOOL)
_add_field(_msg, 'estimated_cost', 8, _descriptor_pb2.FieldDescriptorProto.TYPE_DOUBLE)
_add_field(_msg, 'processing_time_seconds', 9, _descriptor_pb2.FieldDescriptorProto.TYPE_DOUBLE)
_add_field(_msg, 'model', 10, _descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_msg, 'source', 11, _descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_msg, 'version', 12, _descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_msg, 'decision_reason', 13, _descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_msg, 'priority_score', 14, _descriptor_pb2.FieldDescriptorProto.TYPE_DOUBLE)
_add_field(_msg, 'exploit_risk_score', 15, _descriptor_pb2.FieldDescriptorProto.TYPE_DOUBLE)
_add_field(_msg, 'is_novel', 16, _descriptor_pb2.FieldDescriptorProto.TYPE_BOOL)
_add_field(_msg, 'is_duplicate', 17, _descriptor_pb2.FieldDescriptorProto.TYPE_BOOL)

# Register in the default pool
_pool = _descriptor_pool.Default()
DESCRIPTOR = _pool.AddSerializedFile(_file.SerializeToString())

# Build the Python class for EmbeddingEvent
_EMBEDDINGEVENT = DESCRIPTOR.message_types_by_name['EmbeddingEvent']
EmbeddingEvent = _reflection.GeneratedProtocolMessageType(
	'EmbeddingEvent',
	(_message.Message,),
	{
		'DESCRIPTOR': _EMBEDDINGEVENT,
		'__module__': __name__,
	}
)
_sym_db.RegisterMessage(EmbeddingEvent)